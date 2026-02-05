# Egypt Economic Dashboard

A Dash-powered dashboard that tracks Egypt's key economic indicators with near real-time updates and an interactive UI.

**Live Demo:** https://egyptecon.abdelrahmanbahaa.me/

## Highlights

- USD/EGP exchange rate with 1-minute updates
- GDP and inflation series with scheduled refreshes
- EGX30 index live (best-effort, unofficial source)
- PDF report export
- Dockerized for easy local and server deployment

## Screenshots and GIFs

> Add your own screenshots/GIFs to the paths below (see `docs/assets/`).

![Dashboard overview](docs/assets/dashboard.png)
![Live updates](docs/assets/live-demo.gif)

## Tech Stack

- Dash + Plotly
- PostgreSQL
- APScheduler
- Docker + Docker Compose

## Data Sources

- World Bank (GDP, Inflation)
- exchangerate.host (USD/EGP)
- Yahoo Finance (EGX30, unofficial/best-effort)

## Run Locally with Docker

1. **Clone the repo**

```bash
git clone https://github.com/sweetpotatoX/egyptecon_dashboard.git
cd egyptecon_dashboard
```

2. **Start the stack**

```bash
docker compose up -d --build
```

3. **Open the dashboard**

```
http://localhost:8050
```

## Environment Variables

- `DATABASE_URL` (default set in `docker-compose.yml`)
- `EGX30_SYMBOL` (optional override for the Yahoo Finance symbol, default: `^EGX30`)

Example override using Docker Compose:

```yaml
services:
  app:
    environment:
      DATABASE_URL: postgresql://egyptecon:egyptecon_secure_password_change_me@db:5432/egyptecon
      EGX30_SYMBOL: ^EGX30
```

## Deployment (Server)

1. **Clone on your server**

```bash
git clone https://github.com/sweetpotatoX/egyptecon_dashboard.git
cd egyptecon_dashboard
```

2. **Start the stack**

```bash
docker compose up -d --build
```

3. **(Optional) Expose publicly**

- Use your reverse proxy (e.g., Caddy/Nginx) to point to `http://localhost:8050`
- Or use Cloudflare Tunnel with your existing `cloudflared` configuration

## How Updates Work

- USD/EGP: updated every 1 minute
- EGX30: updated every 1 minute (best-effort)
- Full refresh (GDP/Inflation + history): daily at midnight

## Troubleshooting

- **No data on the dashboard:**
  - Check app logs: `docker compose logs -f app`
  - Check DB logs: `docker compose logs -f db`
- **EGX30 shows N/A:**
  - Try a different symbol with `EGX30_SYMBOL`
  - Yahoo Finance data may be delayed/unavailable

## License

MIT
