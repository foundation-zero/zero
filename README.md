# Foundation Zero Docker Environment

This directory contains the Docker Compose configuration for the Foundation Zero platform. The setup is modularized using Docker Compose profiles to allow running specific applications independently.

## Setup

 - Create a `.env` based on `.env.example`.
 - Secrets can be found in Bitwarden

## Profiles

You can start specific applications using the `--profile` flag.

Usage:
```bash
docker compose --profile <profile_name> up
```

### Available Profiles

| Profile | Description | Included Services |
|---------|-------------|-------------------|
| `zero` | Core infrastructure services required for the platform foundation. | MQTT, Postgres, RisingWave, Hasura, Home Assistant |
| `data` | Tools for data generation and DBT model generation. | Core Infra + Data Generators, DBT |
| `data-collection` | Ingestion pipeline for collecting MQTT data and storing time-series data. | Core Infra + Vector, GreptimeDB |
| `domestic` | The Domestic Control application for home automation logic. | Core Infra, Domestic Control API, Control and Stub |
| `loads` | The Loads subsystem for capturing and exposing rigging loads (and other relevated values). | Core Infra, Loads API, Control and Stubs |
| `thrs` | The THRS (Thermal Harvesting & Recovery System) Application stack. | MQTT, THRS Control, THRS Simulation |


*Note: domestic-control-api is a remote schema in Hasura. If Hasura boots before domestic-control-api, it'll not load the remote schema, because it can't verify it through introspection. Use `hasura metadata reload --admin-secret myadminsecretkey` to fix this.*

## Services Overview

### Core Infrastructure
*   **vernemq**: High-performance MQTT broker used for messaging between services and devices.
*   **postgres**: Primary relational database for persistent storage and metadata.
*   **risingwave**: Streaming database for real-time data processing and analytics.
*   **hasura**: GraphQL engine providing an instant API over Postgres and RisingWave.
*   **hass**: Home Assistant instance for home automation integration.
*   **setup-postgres / setup-risingwave**: Initialization containers that configure schemas and sources on startup.

### Data Tools
*   **data-gen**: Python tool to generate synthetic data for testing.
*   **dbt-gen**: Generates DBT models for data transformation.

### Data Collection
*   **vector**: Collects and routes MQTT events into the time-series backend.
*   **greptimedb**: Time-series database used to store and query collected telemetry.

### Domestic Control
*   **domestic-control-api**: GraphQL API service for the domestic control application.
*   **domestic-control-control**: Background worker handling control logic and state management.
*   **domestic-control-stub**: Simulates hardware interfaces (e.g., Termodinamica) for development without physical devices.

### Loads
*   **loads-api**: GraphQL API service for the loads application.
*   **loads-control**: Control logic worker for load management.
*   **loads-pcan-stub**: Simulates PCAN (CAN bus) interfaces.
*   **loads-conditions-stub**: Simulates environmental conditions.
*   **loads-sensor-stub**: Simulates sensor data inputs.

### THRS
*   **thrs-control**: Control logic worker for THRS.
*   **thrs-simulation**: Simulation that models the environment for THRS.
