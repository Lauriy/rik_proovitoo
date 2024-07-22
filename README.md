![Django application](https://github.com/Lauriy/rik_proovitoo/workflows/Django%20application/badge.svg)
[![codecov](https://codecov.io/gh/Lauriy/rik_proovitoo/branch/master/graph/badge.svg)](https://codecov.io/gh/Lauriy/rik_proovitoo)

# Job application homework for Registrite ja Infosüsteemide Keskus

## Load fixtures
Activate your venv
```bash
  docker compose up -d
  python manage.py loaddata rik_proovitöö/fixtures/superuser.json
  python manage.py loaddata rik_proovitöö/fixtures/legal_entity.json
  python manage.py loaddata rik_proovitöö/fixtures/equity.json
```

## Django admin

Visit /admin

Use lauri:mellon after loading fixtures for superuser access.

## Local TDD:

Activate your venv
```bash
    docker compose up -d
    pip install -r requirements.txt -r requirements.test.txt
    pytest
```
Browse the coverage report: file:///home/lauri/PycharmProjects/rik_proovitoo/htmlcov/index.html