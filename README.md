# StarWars API (SWAPI Wrapper) — Case Técnico PowerOfData

API em **Python + FastAPI** que consome a **SWAPI (swapi.dev)** e adiciona valor com:
- **filtros locais** (quando a SWAPI não suporta por campo)
- **ordenação** (asc/desc)
- **seleção de campos** (`fields=...`)
- **expansão de relacionamentos** (`include=...`)
- endpoints **correlacionados** (ex.: personagens de um filme)

> Objetivo: entregar uma experiência mais rica e padronizada para consultas de personagens, planetas, naves e filmes do universo Star Wars.

---

## 1) Visão geral

A aplicação atua como uma camada intermediária (BFF/API Aggregator):
1. Recebe requests do cliente
2. Busca dados na SWAPI
3. Aplica regras locais (filtros/ordenação/include/fields)
4. Retorna uma resposta padronizada, com metadados (`meta`)

---

## 2) Arquitetura

```mermaid
flowchart LR
  U[Cliente] --> G[API Gateway / Apigee]
  G --> CF[Cloud Functions (Python/FastAPI)]
  CF --> SW[SWAPI.dev]
  CF -->|opcional| C[(Cache TTL em memória)]
````

### Componentes

* **API Gateway/Apigee**: roteamento, autenticação e rate limiting (quando habilitado)
* **Cloud Functions (2ª geração)**: execução do backend Python
* **SWAPI**: fonte de dados externa
* **Cache TTL (in-memory)**: reduz chamadas repetidas e melhora latência

---

## 3) Endpoints

### 3.1 Healthcheck

**GET** `/health`

**Response**

```json
{ "status": "ok" }
```

---

### 3.2 Listagem genérica por recurso

**GET** `/v1/resources/{resource}`

Recursos suportados:

* `people`
* `planets`
* `starships`
* `films`

#### Query Params

* `search` (string): repassa para SWAPI `?search=...`
* `page` (int): repassa para SWAPI `?page=...` (padrão: 1)
* `sort` (string): ordena resultados **da página atual** (ex.: `name`)
* `order` (`asc|desc`): direção da ordenação
* `fields` (csv): projeção de campos (ex.: `fields=name,gender`)
* `include` (csv): expande relacionamentos (ex.: `include=homeworld`)

#### Filtros locais (exemplos)

> Observação: a SWAPI não suporta todos os filtros por campo; estes são aplicados localmente na API.

* People: `gender`, `eye_color`, `hair_color`, `min_height`, `max_height`
* Planets: `climate`, `terrain`, `min_population`, `max_population`
* Starships: `starship_class`
* Films: (pode ser expandido conforme necessidade)

---

#### Exemplo 1: buscar Luke

```bash
curl "http://127.0.0.1:8000/v1/resources/people?search=luke"
```

**Response (exemplo)**

```json
{
  "resource":"people",
  "count":1,
  "page":1,
  "page_size":1,
  "next":null,
  "previous":null,
  "results":[{ "name":"Luke Skywalker", "...": "..." }],
  "meta": { "sort": null, "order":"asc", "filters_applied":{}, "included":[] }
}
```

---

#### Exemplo 2: include (expansão do homeworld)

```bash
curl "http://127.0.0.1:8000/v1/resources/people?search=luke&include=homeworld"
```

**Response (trecho)**

```json
{
  "results": [
    {
      "name": "Luke Skywalker",
      "homeworld": {
        "name": "Tatooine",
        "climate": "arid",
        "terrain": "desert"
      }
    }
  ],
  "meta": { "included": ["homeworld"] }
}
```

---

#### Exemplo 3: ordenação por nome (página atual)

```bash
curl "http://127.0.0.1:8000/v1/resources/people?sort=name&order=asc"
```

> Nota: a ordenação é aplicada **nos itens retornados pela SWAPI na página consultada**.

---

### 3.3 Endpoints correlacionados (relações)

#### Personagens de um filme

**GET** `/v1/films/{film_id}/characters`

Query Params:

* `sort` (padrão: `name`)
* `order` (`asc|desc`)
* `fields` (csv)

**Exemplo**

```bash
curl "http://127.0.0.1:8000/v1/films/1/characters?sort=name&fields=name,gender"
```

**Response**

```json
{
  "film_id": 1,
  "film_title": "A New Hope",
  "count": 18,
  "results": [
    { "name": "Beru Whitesun lars", "gender": "female" },
    { "name": "Biggs Darklighter", "gender": "male" }
  ]
}
```

---

## 4) Rodando localmente

### 4.1 Pré-requisitos

* Python 3.10+
* pip

### 4.2 Instalação de dependências

```bash
python3 -m pip install --user -r requirements.txt
```

### 4.3 Executar servidor

```bash
python3 -m uvicorn app.main:app --reload
```

Acessos:

* Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5) Variáveis de ambiente (.env)

Opcional. Se quiser, crie um arquivo `.env`:

```env
SWAPI_BASE_URL=https://swapi.dev/api
HTTP_TIMEOUT_SECONDS=10
CACHE_TTL_SECONDS=120
MAX_INCLUDE_DEPTH=1
```

> Se estiver usando `.env`, execute o uvicorn garantindo carregamento (ou configure no ambiente).
> No GCP, prefira configurar essas variáveis diretamente no serviço (Cloud Functions).

---

## 6) Deploy no GCP (Cloud Functions + API Gateway)

> Observação: existem várias formas de publicar FastAPI no GCP. Para este case, o objetivo é demonstrar arquitetura e entrega.

### 6.1 Cloud Functions (2ª geração)

Passos gerais:

1. Criar um projeto no GCP

2. Habilitar APIs:

   * Cloud Functions
   * Cloud Build
   * Artifact Registry
   * API Gateway (se usar)

3. Fazer deploy da função apontando para o app FastAPI (via container/entrypoint).

> **Sugestão de implementação**: usar Functions Framework / container para expor o FastAPI.

### 6.2 API Gateway

1. Exportar OpenAPI (FastAPI fornece automaticamente):

   * Acesse `http://<host>/openapi.json`
   * Salve e converta para YAML se necessário
2. Criar API Config no API Gateway usando o `openapi.yaml`
3. Apontar o Gateway para a Cloud Function

### 6.3 Autenticação (opcional)

* API Key (no API Gateway) ou JWT (dependendo do nível de segurança desejado)

---

## 7) Rodando testes

### 7.1 Executar

```bash
pytest -q
```

> Os testes cobrem filtros/ordenação e podem ser expandidos para testes de rotas com mock de HTTP (SWAPI).

---

## 8) Decisões técnicas

### Por que FastAPI?

* Alto desempenho e ergonomia
* Tipagem e validação via Pydantic
* Documentação automática (Swagger/OpenAPI), útil para API Gateway

### Por que separar em routers/services/core?

* Facilita manutenção e testes
* Routers: camada HTTP (orquestração)
* Services: regras de negócio (filtros, include, integração SWAPI)
* Core: configuração/infra (logs, erros)

### Por que cache TTL?

* Reduz chamadas repetidas à SWAPI
* Melhora latência e confiabilidade
* Implementação simples e eficiente para o escopo do case

### Por que filtros/ordenação locais?

* A SWAPI tem limitações de filtros por campo
* O case exige capacidade de aplicar regras de negócio além do “proxy”

---

## 9) Próximos passos (melhorias)

* Paginação própria em endpoints correlacionados (ex.: `films/{id}/characters?page=...`)
* Testes de rota com mock HTTP (respx/httpx)
* Rate limit e autenticação no API Gateway
* Observabilidade (request_id, logs estruturados)

```