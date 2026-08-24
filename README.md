# Dataspace Backend

This set of APIs allows for communication between an Apache Fuseki triplestore, a timescaleDB timeseries database, a mongoDB objectstore for trials and KADI4MAT.
The goal is for the end-user to use ontological concepts to retrieve specific data from a timeseries database without knowing the structure of the timescaleDB.

## Installation

### Environment variables

You must set environment variables according to the Fuseki, timescaleDB and mongoDB that you wish to connect to.
Environment variables must be set in order for this API to work properly (see `.env.default`).

These variables can be set by creating a file ".env" that will be read.

### Docker

Ensure the settings in `.env` are correctly set.

Run this code snippet in the terminal to build and run :
```sh
docker compose up --build -d
```
The swagger openapi specification can be found at <http://localhost:8000/docs>

### timescaleDB

In the docker-compose.yaml , we have a sample with its own timescaleDB which can be initialized using [init.sql](timescaledb/init.sql).


### KADI

To enable integration with KADI, you must provide a valid KADI Personal Access Token (PAT) during the Docker build.

Example:

```bash
docker build --build-arg PAT="<YOUR_KADI_PAT>" -t dataspace_backend .
```
