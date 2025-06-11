# Telegram Trading-Calls Feed

This project implements the application described in the "Telegram Trading-Calls Feed" PDR. It aggregates messages from a curated set of public Telegram channels and streams them to a real-time web feed.

## Prerequisites

- Docker and Docker Compose
- Telegram API credentials (`API_ID` and `API_HASH`) from [my.telegram.org](https://my.telegram.org)

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd callers
    ```

2.  **Create your environment file:**
    Copy the `.env.example` file to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```

3.  **Configure your environment variables in `.env`:**
    - Fill in your `API_ID` and `API_HASH`.
    - The `SESSION_STRING` will be generated on the first run of the collector service. You will be prompted to enter your phone number, login code, and password (if you have 2FA enabled).

4.  **Build and run the application:**
    ```bash
    docker compose up --build
    ```

5.  **Access the application:**
    - **Frontend:** [http://localhost:3000](http://localhost:3000)
    - **API:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

- `services/collector`: A Python service using Telethon to connect to Telegram, ingest messages, and store them in the database.
- `services/api`: A Python FastAPI service that serves historical messages via a REST endpoint and real-time messages via a WebSocket.
- `frontend`: A Next.js single-page application that displays the message feed.
- `docker-compose.yml`: Orchestrates all the services.
- `channels.yml`: A simple YAML file located in `services/collector` to configure the list of Telegram channels to monitor.

## Running Tests

To run the test suites for the services, execute the following commands:

```bash
# From the root directory
docker compose run --rm api pytest
docker compose run --rm collector pytest
docker compose run --rm frontend npm test
``` 