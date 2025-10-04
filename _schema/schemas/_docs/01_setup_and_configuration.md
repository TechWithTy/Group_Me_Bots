# Setup and Configuration Guide

## Environment Setup

### 1. Dependencies Installation
```bash
# Core dependencies
pip install pydantic fastapi uvicorn sqlalchemy sqlmodel

# Optional: Database drivers
pip install psycopg2-binary  # PostgreSQL
pip install pymongo          # MongoDB
pip install redis            # Caching

# Development tools
pip install black isort ruff mypy
```

### 2. Project Structure
```
your_project/
├── schemas/                 # Pydantic models
│   ├── __init__.py
│   ├── tenants.py
│   ├── users.py
│   ├── groups.py
│   ├── commerce.py
│   ├── subscriptions.py
│   ├── moderation.py
│   ├── analytics.py
│   ├── monetization.py
│   ├── monetization_advanced.py
│   └── bots.py
├── app/
│   ├── models.py           # SQLModel tables
│   ├── database.py         # Database connection
│   ├── config.py           # Configuration
│   └── middleware.py       # Tenant resolution
└── requirements.txt
```

### 3. Configuration
```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:pass@localhost/db"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "your-secret-key"
    api_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Database Setup

### PostgreSQL with SQLModel
```python
# models.py
from sqlmodel import SQLModel, Field
from schemas.tenants import Tenant

class TenantTable(Tenant, SQLModel, table=True):
    __tablename__ = "tenants"

    class Config:
        arbitrary_types_allowed = True

# Create tables
from sqlmodel import create_engine
engine = create_engine(settings.database_url)
SQLModel.metadata.create_all(engine)
```

### MongoDB with Beanie
```python
# models.py
from beanie import Document
from schemas.tenants import Tenant

class TenantDocument(Tenant, Document):
    class Settings:
        name = "tenants"
```

## API Setup

### FastAPI Integration
```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from schemas.tenants import Tenant

app = FastAPI(title="SaaS GroupMe Bot API")

@app.post("/tenants/", response_model=Tenant)
async def create_tenant(tenant_data: Tenant):
    # Validate with Pydantic
    tenant = Tenant(**tenant_data.dict())

    # Save to database
    # tenant_table = TenantTable(**tenant.dict())
    # db.add(tenant_table)
    # db.commit()

    return tenant

@app.get("/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    # Fetch from database with tenant isolation
    # tenant = db.query(TenantTable).filter(TenantTable.tenant_id == tenant_id).first()
    # if not tenant:
    #     raise HTTPException(status_code=404, detail="Tenant not found")
    # return Tenant(**tenant.__dict__)
    pass
```

## Testing Setup

### Pytest Configuration
```python
# conftest.py
import pytest
from schemas.tenants import Tenant
from schemas.users import User

@pytest.fixture
def sample_tenant():
    return Tenant(
        name="Test Company",
        api_key="test-api-key-123"
    )

@pytest.fixture
def sample_user(sample_tenant):
    return User(
        tenant_id=sample_tenant.id,
        groupme_user_id="user_123",
        nickname="TestUser"
    )
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tenants.py

# Run with coverage
pytest --cov=schemas tests/
```

## Environment Variables

Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/saas_bot
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
API_VERSION=v1
DEBUG=true
```

## Deployment Considerations

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Configuration
```python
# config.py (production)
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    api_version: str = "v1"
    debug: bool = False
    workers: int = 4

    class Config:
        env_file = ".env.prod"
```

## Next Steps

After setup, proceed to:
1. [Multi-Tenancy Implementation](./02_multi_tenancy.md)
2. [Model Relationships and Usage](./03_model_relationships.md)
3. [Analytics and Optimization](./04_analytics_and_optimization.md)
