# MoneyInOne - Backend Requirements Document
## Simple Financial Asset Tracker API

### **Project Overview**
Backend API for MoneyInOne - a simple web-based financial asset tracker that allows users to add, edit, delete, and view their financial assets with multi-currency support and portfolio summary.

---

## **1. Core Requirements from UX Analysis**

### **1.1 Asset Types Supported**
- **Cash** (Savings accounts, checking accounts)
- **Stock** (Individual stocks with ticker symbols)
- **Crypto** (Bitcoin, Ethereum, etc.)
- **Real Estate** (Properties, apartments)
- **Gold** (Physical gold holdings)
- **Bonds** (Government/corporate bonds)
- **Customized**

### **1.2 Key Features**
- Dashboard with portfolio overview and pie chart
- Asset listing grouped by type
- Add/Edit/Delete individual assets
- Multi-currency support (USD, EUR, GBP, JPY, CAD, AUD)
- Portfolio value calculation and display
- Simple asset management with current value tracking

---

## **2. Technology Stack**

### **2.1 Core Framework**
- **FastAPI** (Python 3.11+) - Simple, fast, with automatic docs
- **PostgreSQL** - Reliable database for financial data
- **Redis** - For cache data
- **Pydantic** - Data validation and serialization

### **2.2 Dependencies**
```python
# Core
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
psycopg2-binary = "^2.9.0"
pydantic = "^2.5.0"
redis = "^5.0.1"

# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
```

---

## **3. Database Schema**

### **3.1 Assets Table**
```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,  -- 'cash', 'stock', 'crypto', 'housing', 'gold', 'bonds'
    symbol VARCHAR(20),  -- Optional: stock ticker, crypto symbol
    current_value DECIMAL(15, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL,  -- ISO currency code
    shares DECIMAL(20, 8),  -- Optional: for stocks
    purchase_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **3.2 Exchange Rates Table** (Optional for future)
```sql
CREATE TABLE exchange_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(15, 8) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## **4. API Endpoints**

### **4.1 Asset Management**

#### **GET /api/v1/assets**
```python
# Get all assets grouped by type
Response: {
    "cash": [
        {
            "id": "uuid",
            "name": "USD Savings Account",
            "current_value": 25480.00,
            "currency": "USD",
            "purchase_date": "2024-01-15",
            "updated_at": "2024-12-15T10:00:00Z"
        }
    ],
    "stocks": [
        {
            "id": "uuid", 
            "name": "Apple Inc. (AAPL)",
            "symbol": "AAPL",
            "shares": 150,
            "current_value": 28950.00,
            "currency": "USD",
            "purchase_date": "2024-01-15"
        }
    ],
    "crypto": [...],
    "real_estate": [...],
    "gold": [...],
    "bonds": [...]
}
```

#### **POST /api/v1/assets**
```python
# Create new asset
Request: {
    "name": "Bitcoin",
    "asset_type": "crypto",
    "symbol": "BTC",  # Optional
    "current_value": 21500.00,
    "currency": "USD",
    "shares": 0.5,  # Optional
    "purchase_date": "2024-06-10",
    "description": "Long-term crypto investment"
}

Response: {
    "id": "uuid",
    "message": "Asset created successfully"
}
```

#### **PUT /api/v1/assets/{asset_id}**
```python
# Update existing asset
Request: {
    "name": "Updated Asset Name",
    "current_value": 22000.00,
    "description": "Updated description"
}
```

#### **DELETE /api/v1/assets/{asset_id}**
```python
# Delete asset
Response: {
    "message": "Asset deleted successfully"
}
```

### **4.2 Portfolio Summary**

#### **GET /api/v1/portfolio/summary**
```python
# Get portfolio overview for dashboard
Response: {
    "total_portfolio_value": 284750.32,
    "base_currency": "USD",
    "asset_breakdown": {
        "cash": {"value": 34230.00, "percentage": 12.0, "count": 2},
        "stocks": {"value": 47175.00, "percentage": 16.6, "count": 4},
        "crypto": {"value": 52130.00, "percentage": 18.3, "count": 2},
        "real_estate": {"value": 485000.00, "percentage": 50.4, "count": 1},
        "gold": {"value": 15680.00, "percentage": 5.5, "count": 1},
        "bonds": {"value": 8950.00, "percentage": 3.1, "count": 1}
    },
    "total_assets": 284750.32,
    "total_credits": 27699.68,  # Future feature
    "net_worth": 257050.64,
    "last_updated": "2024-12-15T14:30:00Z"
}
```

### **4.3 Asset Types**

#### **GET /api/v1/asset-types**
```python
# Get supported asset types for form dropdown
Response: {
    "asset_types": [
        {"value": "cash", "label": "Cash"},
        {"value": "stock", "label": "Stock", "requires_symbol": true, "requires_shares": true},
        {"value": "crypto", "label": "Cryptocurrency", "requires_symbol": true},
        {"value": "housing", "label": "Real Estate"},
        {"value": "gold", "label": "Gold"},
        {"value": "bonds", "label": "Bonds"}
    ]
}
```

### **4.4 Currencies**

#### **GET /api/v1/currencies**
```python
# Get supported currencies
Response: {
    "currencies": [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "GBP", "name": "British Pound", "symbol": "£"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
        {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"}
    ]
}
```

---

## **5. Data Models**

### **5.1 Pydantic Schemas**
```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Optional
from enum import Enum

class AssetType(str, Enum):
    CASH = "cash"
    STOCK = "stock"
    CRYPTO = "crypto"
    HOUSING = "housing"
    GOLD = "gold"
    BONDS = "bonds"

class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: AssetType
    symbol: Optional[str] = Field(None, max_length=20)
    current_value: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    shares: Optional[Decimal] = Field(None, gt=0)
    purchase_date: date
    description: Optional[str] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    current_value: Optional[Decimal] = Field(None, gt=0)
    shares: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None

class AssetResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    symbol: Optional[str]
    current_value: Decimal
    currency: str
    shares: Optional[Decimal]
    purchase_date: date
    description: Optional[str]
    created_at: str
    updated_at: str
```

---

## **6. Project Structure**
```
backend/
├── app/
│ ├── api/
│ │ └── v1/
│ │ ├── assets.py # Asset CRUD endpoints
│ │ ├── portfolio.py # Portfolio summary
│ │ └── metadata.py # Asset types, currencies
│ ├── core/
│ │ ├── config.py # Settings
│ │ └── database.py # DB connection
│ ├── models/
│ │ ├── asset.py # SQLAlchemy models
│ │ └── schemas.py # Pydantic schemas
│ ├── services/
│ │ ├── asset_service.py # Business logic
│ │ └── portfolio_service.py
│ └── main.py # FastAPI app
├── tests/
├── alembic/ # Database migrations
├── requirements.txt
└── README.md
```

## **7. Development Phases**

### **Phase 1: Core API**
- ✅ Basic FastAPI setup
- ✅ Database models and migrations
- ✅ Asset CRUD endpoints
- ✅ Basic portfolio summary

### **Phase 2: Enhancement**
- Portfolio calculations and grouping
- Data validation and error handling
- API documentation
- Unit tests

### **Phase 3: Polish**
- Integration with frontend
- Performance optimization
- Deployment setup
- Documentation completion

---

## **8. Testing Strategy**
```python
# Key test cases
- Asset creation with all types
- Asset update and deletion
- Portfolio calculation accuracy
- Currency validation
- Data persistence
- API response formats
```

---

## **9. Deployment**
```yaml
# docker-compose.yml (simplified)
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/moneyinone
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=moneyinone
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```