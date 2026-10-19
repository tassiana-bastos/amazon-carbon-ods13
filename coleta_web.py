"""
Coleta pontual de notícias da Agência Brasil usando Requests e Beautiful Soup.


"""
import csv
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
SITE = "https://agenciabrasil.ebc.com.br"
USER_AGENT = "INFNET-PB-IA/1.0 (projeto acadêmico; coleta respeitosa)"
TIMEOUT = 30

URLS = [
    # Artigos que já faziam parte da coleta
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/devastacao-na-amazonia-pode-quebrar-maior-maquina-de-chuva-do-mundo",
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-08/imazon-aponta-desmatamento-zero-em-60-de-terras-indigenas-na-amazonia",
    # Três novos artigos solicitados
    "https://agenciabrasil.ebc.com.br/geral/noticia/2016-05/amazonia-ameacada-guardioes-lutam-para-manter-floresta-em-pe",
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/competitividade-do-mercado-de-carbono-moderniza-conservacao-florestal",
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-10/incendios-avancam-sobre-o-oeste-do-para-e-deixam-ar-insalubre",
]

PASTA_RAW = BASE_DIR / "data" / "raw"
PASTA_PROCESSED = BASE_DIR / "data" / "processed"
PASTA_RAW.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

ARQUIVO_CSV = PASTA_PROCESSED / "agencia_brasil_meio_ambiente.csv"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.7",
}


def carregar_regras_robots(session: requests.Session) -> tuple[RobotFileParser, int]:
    """Obtém robots.txt e devolve as regras e o intervalo mínimo entre pedidos."""
    robots_url = f"{SITE}/robots.txt"
    response = session.get(robots_url, timeout=TIMEOUT)
    response.raise_for_status()

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(response.text.splitlines())

    # O robots.txt fornecido para este projeto declara Crawl-delay: 10 para *.
    delay = parser.crawl_delay(USER_AGENT)
    if delay is None:
        delay = parser.crawl_delay("*")
    if delay is None:
        delay = 10
    return parser, max(10, int(delay))


def extrair_texto(soup: BeautifulSoup) -> str:
    """Tenta seletores específicos e, em seguida, seletores semânticos comuns."""
    seletores = [
        "div.conteudo-noticia",
        "div.field-name-body",
        "div.article-body",
        "[itemprop='articleBody']",
        "article",
        "main",
    ]
    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if elemento:
            # Remove elementos que não pertencem ao corpo editorial.
            for ruido in elemento.select(
                "script, style, nav, aside, footer, form, .social-share, "
                ".related-content, .publicidade"
            ):
                ruido.decompose()
            texto = elemento.get_text(" ", strip=True)
            if len(texto) >= 150:
                return texto

    # Fallback conservador: usa a meta description, se existir.
    descricao = soup.select_one('meta[name="description"]')
    if descricao and descricao.get("content"):
        return descricao["content"].strip()
    return ""


def extrair_data(soup: BeautifulSoup) -> str:
    """Lê a data de publicação sem assumir um fuso horário fixo."""
    candidatos = [
        soup.select_one('meta[property="article:published_time"]'),
        soup.select_one('meta[name="date"]'),
        soup.select_one('meta[itemprop="datePublished"]'),
        soup.select_one("time[datetime]"),
    ]
    for item in candidatos:
        if not item:
            continue
        valor = item.get("content") or item.get("datetime") or item.get_text(" ", strip=True)
        if not valor:
            continue
        try:
            data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            return data.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return valor.strip()
    return ""


def extrair_noticia(html: str, url: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    titulo_el = soup.select_one("h1") or soup.select_one('meta[property="og:title"]')
    if titulo_el:
        titulo = (
            titulo_el.get("content", "").strip()
            if titulo_el.name == "meta"
            else titulo_el.get_text(" ", strip=True)
        )
    else:
        titulo = ""

    texto = extrair_texto(soup)
    data_publicacao = extrair_data(soup)

    if not titulo:
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title:
            titulo = og_title.get("content", "").strip()

    if not titulo or not texto:
        raise ValueError(
            f"Não foi possível extrair título e corpo da notícia: {url}. "
            "Verifique a estrutura HTML e não tente contornar bloqueios da fonte."
        )

    return {
        "titulo": titulo,
        "data_publicacao": data_publicacao,
        "texto": texto,
        "url": url,
        "origem": "Agência Brasil",
    }


def main() -> None:
    session = requests.Session()
    session.headers.update(HEADERS)

    print("A consultar robots.txt...")
    regras, crawl_delay = carregar_regras_robots(session)
    print(f"robots.txt consultado. Intervalo mínimo entre pedidos: {crawl_delay}s.")

    # Validar domínio e permissões antes de descarregar qualquer artigo.
    for url in URLS:
        if urlparse(url).netloc != urlparse(SITE).netloc:
            raise ValueError(f"URL fora do domínio esperado: {url}")
        if not regras.can_fetch(USER_AGENT, url):
            raise PermissionError(
                f"robots.txt não autoriza a recolha desta URL: {url}. "
                "A recolha foi interrompida sem tentar contornar a regra."
            )

    noticias = []
    erros = []

    for indice, url in enumerate(URLS, start=1):
        print(f"\n[{indice}/{len(URLS)}] A consultar: {url}")
        try:
            response = session.get(url, timeout=TIMEOUT)
            print(f"HTTP {response.status_code}")
            response.raise_for_status()

            # Guardar uma cópia do HTML bruto para rastreabilidade.
            arquivo_html = PASTA_RAW / f"agencia_brasil_noticia_{indice}.html"
            arquivo_html.write_text(response.text, encoding=response.encoding or "utf-8")

            noticia = extrair_noticia(response.text, url)
            noticias.append(noticia)
            print(f"Extraído: {noticia['titulo']}")
        except (requests.RequestException, ValueError) as exc:
            erros.append((url, str(exc)))
            print(f"ERRO: {exc}")

        # Cumprir o intervalo indicado, mesmo se um artigo falhar.
        if indice < len(URLS):
            print(f"A aguardar {crawl_delay}s antes do próximo pedido...")
            time.sleep(crawl_delay)

    if erros:
        print("\nAlgumas páginas não foram processadas:")
        for url, erro in erros:
            print(f"- {url}: {erro}")
        print("O CSV não será sobrescrito parcialmente. Corrija/verifique as URLs e execute novamente.")
        raise RuntimeError(f"Falha na coleta de {len(erros)} página(s).")

    campos = ["titulo", "data_publicacao", "texto", "url", "origem"]
    with ARQUIVO_CSV.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(noticias)

    print("\nColeta concluída.")
    print(f"Notícias processadas: {len(noticias)}")
    print(f"CSV: {ARQUIVO_CSV}")


if __name__ == "__main__":
    main()
