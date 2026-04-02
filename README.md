# MoneyInOne 🦞

Monitor all your assets and credits across multiple currencies with real-time updates.

> 🦞 Maintained by [openclaw](https://github.com/openclaw) — the AI engineering team behind MoneyInOne.

## Architecture

- **Backend**: FastAPI + PostgreSQL + Redis, deployed on Render
- **Frontend**: iOS app (Swift)

## Infrastructure & Costs

Hosted on [Render](https://render.com). Current monthly costs:

| Service | Plan | Cost/month |
|---|---|---|
| Web Service (`moneyinone-api`) | Starter | $7.00 |
| PostgreSQL (`moneyinone-db`) | Basic 256MB | $7.00 |
| Redis (`moneyinone-redis`) | Free Tier | $0.00 |
| **Total** | | **~$14.00/mo** |

> ⚠️ Render suspends paid services if billing lapses. Keep payment method active to avoid downtime.

## Live URL

- API: https://moneyinone-api.onrender.com
- Health check: https://moneyinone-api.onrender.com/health

## Local Development

See `backend/` for setup instructions and `backend/env.example` for required environment variables.
