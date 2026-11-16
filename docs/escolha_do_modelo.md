# Escolha e integração do modelo local — TP4

**Projeto:** Amazônia Legal | ODS 13  
**Modelo escolhido:** `Qwen/Qwen2.5-1.5B-Instruct`  
**Tarefa nesta entrega:** classificação temática de textos ambientais.

## 1. Adequação ao projeto

O projeto já reúne duas fontes que contêm texto: notícias da Agência Brasil e, futuramente, observações textuais de usuários. Para o TP4, a tarefa implementada é classificar o assunto de um texto em uma categoria ambiental: `desmatamento`, `queimadas`, `conservacao`, `mudancas_climaticas` ou `outros`. Essa entrega é uma primeira funcionalidade de NLP e não implementa ainda o Q&A/RAG planejado no Project Charter.

## 2. Critérios de escolha

### Desempenho e adequação da tarefa

Foi escolhido um modelo instruction-tuned de geração de texto, capaz de seguir uma instrução em português e escolher uma das categorias com base nas definições fornecidas no prompt. O cartão do Hugging Face descreve o Qwen2.5-1.5B-Instruct como modelo causal instruction-tuned, com 1,54 bilhão de parâmetros e suporte multilíngue que inclui português. Isso o torna mais adequado a uma classificação por instrução do que um modelo exclusivamente de preenchimento de máscara.

A decisão considera também a aula 15–16: o professor recomenda não escolher apenas pelo número de downloads ou pelo nome do modelo. A escolha deve ser justificada pela tarefa real, testada com exemplos do próprio domínio e acompanhada de medição de custo. A aula apresenta o Qwen2.5-1.5B-Instruct como o candidato com melhor resultado no banco de provas demonstrado pelo professor (27/30), mas esse resultado pertence aos relatos e à máquina utilizados na aula, não é uma medição deste projeto.

**Limitação:** ainda é necessário montar um pequeno banco de exemplos ambientais rotulados manualmente e medir acertos/erros na máquina da aluna. A pontuação `confianca` retornada pelo código atual é apenas indicativa/heurística; não é uma probabilidade calibrada.

### Custo computacional local

O modelo possui 1,54B de parâmetros. A aula 15–16 mostra que o custo depende do tipo numérico, da CPU/GPU e do hardware: o professor mediu tempos e memória diferentes entre `float16` e `float32`, e ressalta que os números de uma máquina não devem ser tratados como universais.

Nesta integração, o carregamento é em `float32` na CPU para priorizar compatibilidade. Como estimativa teórica, apenas os pesos em float32 exigem aproximadamente 1,54 bilhão × 4 bytes, ou cerca de 6,2 GB; a memória real de execução será maior por causa de tokenizer, buffers e estruturas auxiliares. Portanto, recomenda-se uma máquina com pelo menos 8 GB de RAM livres para testar, preferencialmente 16 GB. Esse é um requisito prático estimado, não uma garantia de execução.

**Medição a registrar após executar:** processador, RAM, GPU (se houver), tempo de carregamento e tempo médio de cada requisição. Não se deve copiar os tempos medidos pelo professor como se fossem os tempos desta máquina.

### Acessibilidade local

O modelo está disponível publicamente no Hugging Face e o cartão indica licença Apache 2.0. O download é executado separadamente por `python -m src.baixar_modelo`. A API carrega os arquivos do diretório local com `local_files_only=True`, impedindo que a inicialização dependa de uma chamada de inferência à nuvem. Depois do download, a classificação é executada localmente usando `transformers` e `torch`.

Fonte do modelo: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct

## 3. Plano B

Se o modelo não couber na memória ou ficar lento, o primeiro ajuste é testar o modelo menor `Qwen/Qwen2.5-0.5B-Instruct` com o mesmo conjunto de testes. A troca exige repetir a medição de qualidade e tempo; um modelo menor não deve ser presumido equivalente. Outra alternativa simples é manter a rota e devolver HTTP 503 quando o modelo não estiver disponível, sem derrubar as rotas de consulta já existentes.

## 4. Arquitetura da integração

1. `src/baixar_modelo.py` baixa tokenizer e pesos uma única vez para `models/qwen2.5-1.5b-instruct/`.
2. `api/main.py` carrega o modelo no `lifespan` da FastAPI, uma vez na inicialização, e limpa a referência ao encerrar.
3. A rota `POST /processar_texto` recebe `PedidoAnalise` (Pydantic), executa a classificação e retorna `ResultadoAnalise` via `response_model`.
4. A página `pages/ia_ambiental.py` envia o texto por HTTP para a API local e apresenta o resultado/erros ao usuário.

O modelo é carregado durante o `lifespan`, mas uma falha de carregamento não derruba a API. A rota de análise responde 503 enquanto o motor não estiver disponível. A rota é declarada com `def`, porque a inferência é processamento de CPU e não uma espera assíncrona de rede, conforme a explicação da aula 15–16.

## 5. Testes recomendados

- Texto sobre corte de árvores e perda de floresta: esperar `desmatamento`.
- Texto sobre fumaça e incêndio florestal: esperar `queimadas`.
- Texto sobre restauração e proteção de área: esperar `conservacao`.
- Texto sobre aquecimento global e emissões: esperar `mudancas_climaticas`.
- Texto ambiental fora dos quatro temas: pode retornar `outros`.
- Texto com menos de 15 caracteres ou campo adicional: HTTP 422.
- API iniciada sem diretório do modelo: `/saude` deve responder com `modelo_carregado=false` e o POST deve responder 503.

Os resultados devem ser anotados. O classificador é uma ferramenta exploratória e não substitui validação por especialista.
