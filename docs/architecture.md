## MoneyInOne Architecture

### System overview

```mermaid
flowchart LR
    subgraph iOS_App[MoneyInOne iOS App (SwiftUI)]
        VM[ViewModels]
        V[Views]
        APIClient[APIService.swift]
        V --> VM --> APIClient
    end

    subgraph Backend[FastAPI Backend]
        App[FastAPI app (app/main.py)]
        Router[v1 Router (api/v1/router.py)\n- assets\n- credits\n- portfolio\n- metadata\n- health]
        Services[Services Layer\n- FinanceService\n- MarketDataService]
        Core[Core\n- config.py (Settings)\n- database.py (Async SQLAlchemy)]
        Models[Models\n- user, asset, asset_type\n- credit, credit_type\n- Pydantic schemas]
        App --> Router --> Services
        App --> Core
        Services --> Models
        Services --> Core
    end

    subgraph Data_Infra[Data & Infra]
        DB[(SQLite/PostgreSQL)]
        Cache[(Redis)]
        ExtAPI[[Alpha Vantage API]]
        Docker[(docker-compose)]
        Core --> DB
        MarketDataService[MarketDataService] --> Cache
        MarketDataService --> ExtAPI
    end

    iOS_App <-- HTTP/JSON --> Backend
    Backend <-- SQL/Async --> DB
    Backend <-- TCP --> Cache
    Docker --- Backend
    Docker --- Cache
```

### Backend component view

```mermaid
flowchart TD
    FastAPI[FastAPI app\napp/main.py]
    Router[APIRouter\napi/v1/router.py]
    AssetsEP[assets.py]
    CreditsEP[credits.py]
    PortfolioEP[portfolio.py]
    MetadataEP[metadata.py]
    HealthEP[health.py]

    Finance[FinanceService\nbusiness logic]
    Market[MarketDataService\nprice + FX + cache]

    Config[Settings\ncore/config.py]
    DB[Async SQLAlchemy\ncore/database.py]
    Models[ORM + Schemas\napp/models]

    FastAPI --> Router
    Router --> AssetsEP --> Finance
    Router --> CreditsEP --> Finance
    Router --> PortfolioEP --> Finance
    Router --> MetadataEP --> Finance
    Router --> HealthEP

    Finance --> DB
    Finance --> Models
    Finance --> Market
    Market --> Config
    Market --> DB
    Market --> Redis[(Redis cache)]
    Market --> Alpha[[Alpha Vantage]]

    Config --> FastAPI
    Config --> DB
```

### App workflows

#### High‑level user workflow

```mermaid
flowchart TD
    A[App Launch] --> B[Health check /api/v1/health]
    B --> C[Load metadata /api/v1/metadata: currencies, categories]
    C --> D[Fetch lists: /assets, /credits]
    D --> E[Render Dashboard]

    E -->|Add Asset| F[Open Add Form]
    F --> G[POST /api/v1/assets]
    G --> H[Persist via FinanceService -> DB]
    H --> I[Reload lists -> Update UI]

    E -->|Edit/Delete| J[PUT/DELETE /api/v1/assets/{id}]
    J --> H

    E -->|Refresh Prices| K[POST /api/v1/assets/refresh]
    K --> L[FinanceService -> MarketDataService]
    L --> M[Redis cache hit?]
    M -->|Yes| N[Use cached prices]
    M -->|No| O[Call Alpha Vantage]
    O --> P[Cache prices in Redis]
    N --> Q[Update current amounts in DB]
    P --> Q
    Q --> I

    E -->|Portfolio Summary| R[GET /api/v1/portfolio/summary?base_currency=USD]
    R --> S[FinanceService loads assets/credits]
    S --> T[Convert with FX via MarketDataService (cache/API)]
    T --> U[Compute totals & net worth]
    U --> V[Return summary -> UI cards/charts]
```

#### Request/response sequence: Refresh Prices

```mermaid
sequenceDiagram
    participant U as User
    participant V as iOS ViewModel
    participant A as APIService (iOS)
    participant R as FastAPI Router
    participant F as FinanceService
    participant M as MarketDataService
    participant C as Redis
    participant X as Alpha Vantage
    participant D as DB

    U->>V: Tap "Refresh Prices"
    V->>A: POST /api/v1/assets/refresh
    A->>R: HTTP request
    R->>F: refresh_prices(device_id, ids?)
    F->>D: Query tracked assets
    F->>M: update_multiple_assets(assets, base_currency)
    M->>C: GET cache for each symbol
    alt cache miss
        M->>X: Fetch price/FX
        X-->>M: JSON price/FX
        M->>C: SET price with TTL
    end
    M-->>F: {asset_id: (success, price, current_amount)}
    F->>D: Update amounts, last_price_update
    D-->>F: committed
    F-->>R: {updated, failed, skipped}
    R-->>A: 200 OK JSON
    A-->>V: Parsed result
    V-->>U: UI toast + refreshed list
```

#### Request/response sequence: Portfolio Summary

```mermaid
sequenceDiagram
    participant U as User
    participant V as iOS ViewModel
    participant A as APIService (iOS)
    participant R as FastAPI Router
    participant F as FinanceService
    participant M as MarketDataService
    participant D as DB
    participant C as Redis
    participant X as Alpha Vantage

    U->>V: Open Dashboard / Summary
    V->>A: GET /portfolio/summary?base_currency=USD
    A->>R: HTTP request
    R->>F: get_portfolio_summary(device_id, USD)
    F->>D: Load all assets & credits
    loop each item
        F->>M: get_exchange_rate(item.currency -> USD)
        M->>C: GET FX cache
        alt cache miss
            M->>X: Fetch FX
            X-->>M: FX JSON
            M->>C: SET FX with TTL
        end
        F->>F: convert + accumulate totals
    end
    F-->>R: PortfolioSummary(net_worth, breakdowns, last_updated)
    R-->>A: 200 OK JSON
    A-->>V: Parsed summary
    V-->>U: Render cards/charts
```


