# importacao das bibliotecas necessarias

import csv
import requests
import time

from pathlib import Path
from urllib.robotparser import RobotFileParser  
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

SITE = "https://agenciabrasil.ebc.com.br"

USER_AGENT = "INFNET-PB-IA/1.0"

URLS = [
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/devastacao-na-amazonia-pode-quebrar-maior-maquina-de-chuva-do-mundo",
    "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-08/imazon-aponta-desmatamento-zero-em-60-de-terras-indigenas-na-amazonia"
]


PASTA_RAW= Path("data/raw")
PASTA_PROCESSED= Path("data/processed")

PASTA_RAW.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

ARQUIVO_CSV= PASTA_PROCESSED / "agencia_brasil_meio_ambiente.csv"

# Header para a requisicao HTTP
HEADERS = {
    "User-Agent": USER_AGENT
}

# ============================================================
# 2. VERIFICAR ROBOTS.TXT
# ============================================================

print("Verificando o arquivo robots.txt do site...")

resposta_robots = requests.get(f"{SITE}/robots.txt", headers=HEADERS, timeout=30)

resposta_robots.raise_for_status()

regras = RobotFileParser()
regras.parse(resposta_robots.text.splitlines())

crawl_delay = regras.crawl_delay(USER_AGENT)

if crawl_delay is None:
    crawl_delay = 0

print("robots.txt carregado com sucesso.")

print(f"Crawl-delay definido para {crawl_delay} segundos.")

# ============================================================
# 3. VERIFICAR PERMISSÃO DAS URLs
# ============================================================

for url in URLS:

    permitido= regras.can_fetch(USER_AGENT, url)

    print()
    print(f"URL: {url}")
    print(f"Permitido: {permitido}")

    if not permitido:
        raise RuntimeError(f"Raspagem de dados não permitida para a URL: {url}")

# ============================================================
# 4. BAIXAR E SALVAR O HTML
# ============================================================

for indice, url in enumerate(URLS, start=1):

    print()
    print("=" * 60)
    print(f"Baixando pagina {indice} de {len(URLS)}")
    print("=" * 60)

    print(f"URL: {url}")

    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print(f"Status HTTP: {resposta.status_code}")

    resposta.raise_for_status()

    html = resposta.text

    # Nome do arquivo HTML bruto
    arquivo_html = PASTA_RAW / f"noticia_{indice}.html"

    arquivo_html.write_text(
        html,
        encoding="utf-8"
    )

    print(f"HTML salvo em: {arquivo_html}")

    # Respeita o Crawl-delay antes da proxima requisicao
    if indice < len(URLS):

        print(
            f"Aguardando {crawl_delay} segundos "
            "antes da proxima requisicao..."
        )

        time.sleep(crawl_delay)
print()
print("Coleta inicial concluida.")

# ============================================================
# 5. EXTRAIR OS DADOS COM BEAUTIFUL SOUP
# ============================================================

noticias= []


for indice, url in enumerate(URLS, start=1):

    arquivo_html= PASTA_RAW / f"noticia_{indice}.html"

    html= arquivo_html.read_text(
        encoding="utf-8"
    )

    sopa= BeautifulSoup(
        html, 
        "html.parser"
    )

    # --------------------------------------------------------
    # Título
    # --------------------------------------------------------

    titulo= sopa.find("h1")

    if titulo is not None:
        titulo= titulo.get_text(
            " ", 
            strip=True
        )
    else:
        titulo= ""

    # --------------------------------------------------------
    # Data de publicação
    # --------------------------------------------------------

    data = sopa.select_one(
    'meta[property="article:published_time"]'
    ) 
    if data is not None:

        data_original= data.get("content")

        data_publicacao = (
        datetime.fromisoformat(data_original)
        - timedelta(hours=3)
    ).strftime("%d/%m/%Y - %H:%M")
        
    else:
        data_publicacao= ""

    # --------------------------------------------------------
    # Texto da notícia
    # --------------------------------------------------------

    conteudo= sopa.select_one(
        "div.conteudo-noticia"
    )

    if conteudo is not None:
        texto= conteudo.get_text(
            " ", 
            strip=True
        )
    else:
        texto= ""

    # --------------------------------------------------------
    # Verificação
    # --------------------------------------------------------

    if not titulo or not texto:
        raise RuntimeError(
            f"Não foi possível extrair os dados da página: {url}"
        )


    # --------------------------------------------------------
    # Armazenar notícia
    # --------------------------------------------------------

    noticias.append({
        "titulo": titulo,
        "data_publicacao": data_publicacao,
        "texto": texto,
        "url": url
    })


# ============================================================
# 6. SALVAR OS DADOS EM CSV
# ============================================================

with open(
    ARQUIVO_CSV,
    "w",
    encoding="utf-8-sig",
    newline=""
     ) as arquivo:

    campos = [
        "titulo",
        "data_publicacao",
        "texto",
        "url"
    ]

    escritor = csv.DictWriter(
        arquivo,
        fieldnames=campos
    )

    escritor.writeheader()

    escritor.writerows(noticias)


print()
print("=" * 60)
print("CSV GERADO COM SUCESSO")
print("=" * 60)

print(f"Arquivo: {ARQUIVO_CSV}")
print(f"Quantidade de noticias: {len(noticias)}")