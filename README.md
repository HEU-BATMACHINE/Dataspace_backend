# Dataspace Backend

The Dataspace Backend provides a unified API layer for communication between an Apache Fuseki triplestore, a TimescaleDB time-series database, a MongoDB object store for trial data, and KADI4MAT.

Its primary objective is to enable end users to retrieve data from the time-series database using ontology-based concepts, without requiring knowledge of the underlying TimescaleDB schema or database structure.

## Installation

### Environment variables

Before starting the application, configure the required environment variables for the Apache Fuseki, TimescaleDB, and MongoDB instances you intend to use.

These variables are required for the API to function correctly. Refer to .env.default for the complete list of supported configuration options.

You can define the variables by creating a .env file in the project root directory.

### Docker

Ensure that all required settings in the .env file have been configured correctly.

Build and start the application using:
```sh
docker compose up --build -d
```
Once the service is running, the OpenAPI/Swagger documentation is available at: <http://localhost:8000/docs>

### TimescaleDB

The provided docker-compose.yaml includes an example TimescaleDB instance for development and testing purposes.

This database can be initialized using the SQL script located at: [init.sql](timescaledb/init.sql).


### KADI

To enable integration with KADI4MAT, a valid KADI Personal Access Token (PAT) must be provided during the Docker image build process.

Example:

```bash
docker build --build-arg PAT="<YOUR_KADI_PAT>" -t dataspace_backend .
```
