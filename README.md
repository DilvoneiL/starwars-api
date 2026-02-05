# StarWars API (SWAPI Wrapper)

### Case Técnico — PowerOfData

API backend desenvolvida em **Python + FastAPI** que consome a **SWAPI (swapi.dev)** e adiciona uma camada de valor com:

- filtros locais (além das capacidades da SWAPI)
- ordenação (`asc|desc`)
- projeção de campos (`fields=...`)
- expansão de relacionamentos (`include=...`)
- endpoints correlacionados (ex.: personagens de um filme)
- cache TTL em memória
- testes automatizados com mock HTTP
- deploy no GCP com Cloud Functions (2ª gen) + API Gateway

> **Objetivo do case**  
> Demonstrar domínio de backend Python, integração com APIs externas, aplicação de regras de negócio, boas práticas de arquitetura, testes automatizados e deploy no Google Cloud Platform.

---

## 1) Visão Geral

A aplicação atua como uma **API intermediária / BFF (Backend For Frontend)**:

1. Recebe requisições do cliente
2. Consulta dados na SWAPI
3. Aplica regras de negócio locais (filtros, ordenação, include, fields)
4. Retorna respostas padronizadas, com metadados consistentes

Essa abordagem permite oferecer uma experiência mais rica, previsível e controlada do que o consumo direto da SWAPI.

---

## 2) Arquitetura

```mermaid
flowchart LR
  U[Cliente] --> G[API Gateway]
  G --> CF[Cloud Functions 2ª gen / Cloud Run]
  CF --> SW[SWAPI.dev]
  CF -->|opcional| C[(Cache TTL em memória)]
````

### Componentes

* **API Gateway**

  * Roteamento HTTP
  * Camada de entrada pública
  * Possibilidade de autenticação, rate limiting e controle de acesso

* **Cloud Functions (2ª geração)**

  * Execução do backend Python
  * FastAPI adaptado via **ASGI → WSGI (a2wsgi)**

* **SWAPI**

  * Fonte de dados externa

* **Cache TTL (in-memory)**

  * Reduz chamadas repetidas à SWAPI
  * Melhora latência e estabilidade

---

## 3) URLs do serviço

### Via API Gateway (URL principal para consumo)

```text
https://starwars-gw-4pd5e11l.uc.gateway.dev
```

### Backend direto (Cloud Run / Cloud Functions)

```text
https://starwars-api-368671327689.us-central1.run.app
```

> 🔎 **Observação importante**
> O backend pode ser acessado diretamente, mas **o consumo recomendado é via API Gateway**, conforme solicitado no desafio.

---

## 4) Endpoints

### 4.1 Healthcheck

**GET** `/health`

```json
{ "status": "ok" }
```

Exemplo (via Gateway):

```bash
curl https://starwars-gw-4pd5e11l.uc.gateway.dev/health
```

---

### 4.2 Listagem genérica por recurso

**GET** `/v1/resources/{resource}`

Recursos suportados:

* `people`
* `planets`
* `starships`
* `films`

#### Query Params

| Parâmetro | Tipo   | Descrição                           |                      |
| --------- | ------ | ----------------------------------- | -------------------- |
| `search`  | string | Repassado para a SWAPI (`?search=`) |                      |
| `page`    | int    | Página da SWAPI (default: 1)        |                      |
| `sort`    | string | Campo para ordenação local          |                      |
| `order`   | `asc   | desc`                               | Direção da ordenação |
| `fields`  | csv    | Projeção de campos                  |                      |
| `include` | csv    | Expansão de relacionamentos         |                      |

---

#### Filtros locais (exemplos)

> A SWAPI não suporta todos os filtros por campo; estes são aplicados localmente.

* **People**: `gender`, `eye_color`, `hair_color`, `min_height`, `max_height`
* **Planets**: `climate`, `terrain`, `min_population`, `max_population`
* **Starships**: `starship_class`
* **Films**: extensível conforme necessidade

---

#### Exemplo — Buscar Luke (via Gateway)

```bash
curl "https://starwars-gw-4pd5e11l.uc.gateway.dev/v1/resources/people?search=luke"
```

---

#### Exemplo — Include (expansão de relacionamento)

```bash
curl "https://starwars-gw-4pd5e11l.uc.gateway.dev/v1/resources/people?search=luke&include=homeworld"
```

---

### 4.3 Endpoints correlacionados

#### Personagens de um filme

**GET** `/v1/films/{film_id}/characters`

Query Params:

* `sort` (default: `name`)
* `order` (`asc|desc`)
* `fields` (csv)
* `page` (default: 1)
* `page_size` (default: 10)

```bash
curl "https://starwars-gw-4pd5e11l.uc.gateway.dev/v1/films/1/characters?sort=name&order=asc&fields=name,gender&page=1&page_size=5"
```

---

## 5) Execução local

### Pré-requisitos

* Python 3.10+
* pip

### Instalação

```bash
python3 -m pip install -r requirements.txt
```

### Subir servidor

```bash
python3 -m uvicorn app.main:app --reload
```

* Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 6) Variáveis de ambiente

```env
SWAPI_BASE_URL=https://swapi.dev/api
HTTP_TIMEOUT_SECONDS=10
CACHE_TTL_SECONDS=120
MAX_INCLUDE_DEPTH=1
```

No GCP, essas variáveis são configuradas diretamente no serviço.

---

## 7) Testes

Os testes utilizam:

* pytest
* FastAPI TestClient
* respx (mock de chamadas HTTP externas)

Execução:

```bash
pytest -q
```

Os testes garantem:

* isolamento da SWAPI
* semântica correta de erros (404 vs 502)
* filtros, ordenação, paginação e includes

---

## 8) Deploy no GCP (resumo)

### Cloud Functions (2ª geração)

* FastAPI adaptado via **a2wsgi**
* Entry point exposto via **Functions Framework**

Fluxo:

1. Criar projeto no GCP
2. Habilitar APIs necessárias
3. Deploy da função HTTP
4. Obter URL pública

### API Gateway

1. Exportar OpenAPI (`/openapi.json`)
2. Converter para `openapi.yaml` (OpenAPI 3.0.x)
3. Criar API Config e Gateway apontando para a Cloud Function
4. (Opcional) configurar API Key / rate limit

---

## 9) Decisões Técnicas

* **FastAPI** pela produtividade e OpenAPI automático
* **Separação em camadas** (`routers`, `services`, `core`)
* **Cache TTL** para reduzir latência e dependência externa
* **Testes com mock HTTP** para confiabilidade e velocidade

```