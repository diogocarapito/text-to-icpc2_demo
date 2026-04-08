# text-to-icpc2 demo

Streamlit demo of text-to-icpc2 classification model to clasify diagnosis into icpc2 codes.

Model available here: [https://huggingface.co/diogocarapito/text-to-icpc2](https://huggingface.co/diogocarapito/text-to-icpc2)

Training dataset here: [https://huggingface.co/datasets/diogocarapito/text-to-icpc2](https://huggingface.co/datasets/diogocarapito/text-to-icpc2)

Code here: [https://github.com/DiogoCarapito/text-to-icpc2](https://github.com/DiogoCarapito/text-to-icpc2)

Demo deployed here: [https://text-to-icpc2demo.streamlit.app](https://text-to-icpc2demo.streamlit.app)

[![Github Actions Workflow](https://github.com/DiogoCarapito/text-to-icpc2_demo/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/text-to-icpc2_demo/actions/workflows/main.yaml)

## cheat sheet

### venv

```bash
python3.12 -m venv .venv &&
source .venv/bin/activate
```

### Dockerfile

#### build

```bash
docker build -t app:latest .
````

#### check image id

```bash
docker images
````

#### run with image id

```bash
docker run -p 8501:8501 app:latest
````


#run test

## Build images and start both containers in detached mode
docker compose up --build -d

## Check container status
docker compose ps

## Check logs (all services)
docker compose logs

## Check logs for a specific service
docker compose logs app
docker compose logs db

## Test DB connection and insert from inside the app container
docker compose exec app python -c "
import os, psycopg2
conn = psycopg2.connect(
    host=os.environ.get('POSTGRES_HOST', 'localhost'),
    dbname=os.environ.get('POSTGRES_DB', 'icpc2'),
    user=os.environ.get('POSTGRES_USER', 'icpc2user'),
    password=os.environ.get('POSTGRES_PASSWORD', ''),
)
print('Connected OK')
"

## List tables in the DB
docker compose exec db psql -U icpc2user -d icpc2 -c "\dt"

## Query the predictions table
docker compose exec db psql -U icpc2user -d icpc2 -c "SELECT * FROM predictions;"

## Rebuild and restart only the app (after code changes, without touching the db)
docker compose up --build -d app

## Stop everything
docker compose down

## Stop and wipe the DB volume (full reset)
docker compose down -v


sudo apt update && sudo apt upgrade -y

apt  install docker.io

git clone https://github.com/diogocarapito/text-to-icpc2_demo

cd text-to-icpc2_demo


