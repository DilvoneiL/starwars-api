starwars-api/
  app/
    main.py               # FastAPI entry
    routers/
      resources.py
      relations.py
    services/
      swapi_client.py     # chamadas externas
      enrich.py           # include/expansões
      filters.py          # filtros locais
      sorting.py
      cache.py
    models/
      schemas.py          # Pydantic
    core/
      config.py
      errors.py
      logging.py
  tests/
    test_resources.py
    test_relations.py
    test_filters_sort.py
  openapi.yaml            # usado no API Gateway
  requirements.txt
  README.md
