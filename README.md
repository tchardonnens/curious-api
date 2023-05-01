# Curious API
Knowledge portal backend with FastAPI

---

## Manage packages

This projects uses Python 3.11 and pipenv package manager. Take care to enable pipenv BEFORE trying to run the project. All the dependencies are in it.

Install pipenv

`pip install --user pipenv`

Install project packages

`pipenv sync`

Enable pipenv

`pipenv shell`

Run a command using packages in pipenv

`pipenv run` + command

---

## Setup databases


Orchestration is made using docker compose.

Please install Docker desktop: https://www.docker.com/products/docker-desktop/

Afterwards, make sure Docker compose V2 is enabled in the parameters (Settings > General > Use Docker Compose V2)


Run Redis and PSQL

`docker compose up -d`

Stop all compose containers

`docker compose stop`

---

## RUN THE PROJECT (OMG)


To run the python server

`pipenv run uvicorn main:app --reload`

To stop it

`CTRL+C`



