# Manual Pre-Deployment Checklist

This file outlines the necessary manual steps to be completed before deploying the application to a production environment.

## 1. Configure Environment Variables

You must create a `.env` file in the root of the project by copying the example file:

```bash
cp .env.example .env
```

Then, edit the `.env` file and provide the following secret values:

-   **`API_ID`**: Your personal Telegram Application ID.
-   **`API_HASH`**: Your personal Telegram Application Hash.

You can get these values by creating an application on [my.telegram.org](https://my.telegram.org).

## 2. Generate Telegram Session String

The `collector` service needs to authenticate with your Telegram account to listen to channel messages. The first time you run the application, it will prompt you for your phone number, the code you receive, and your two-factor authentication password (if enabled).

1.  **Run the collector service interactively to generate the session string:**
    ```bash
    docker compose run --rm collector
    ```

2.  **Follow the prompts in your terminal to log in.**

3.  Once you successfully log in, a **session string** will be printed to your console. It will be a long, seemingly random string of characters.

4.  **Copy this entire session string.**

5.  **Paste the copied string into your `.env` file** as the value for the `SESSION_STRING` variable:
    ```
    SESSION_STRING=your_long_session_string_here...
    ```

6.  With the session string saved, the collector can now start non-interactively. You can restart the full application stack:
    ```bash
    docker compose up --build -d
    ```

## 3. Review and Customize Channel List

The list of Telegram channels to monitor is defined in `services/collector/channels.yml`.

-   **Edit this file** to include the public channel usernames or invite links you wish to track.

```yaml
# services/collector/channels.yml
channels:
  - "some_crypto_channel"
  - "another_public_channel_link"
  - "etc"
```

## 4. Production Hardening (Next Steps)

For a true production deployment, consider the following:

-   **Secure Secret Management**: Move secrets (`API_ID`, `API_HASH`, `SESSION_STRING`, `POSTGRES_PASSWORD`) from the `.env` file to a secure secret management service (e.g., AWS Secrets Manager, HashiCorp Vault, or your cloud provider's equivalent).
-   **HTTPS**: Configure a reverse proxy (like Nginx or Traefik) to handle incoming traffic and provide SSL/TLS termination (HTTPS) for the frontend and API.
-   **Database**: Use a managed PostgreSQL service (like Amazon RDS or Google Cloud SQL) instead of a containerized instance for better scalability, backups, and reliability.
-   **Logging & Monitoring**: Set up a centralized logging and monitoring solution (like the proposed Loki/Prometheus/Grafana stack) to track application health and performance.
-   **CI/CD**: Complete the CI/CD pipeline in `.github/workflows/ci.yml` to automate testing and deployments. 