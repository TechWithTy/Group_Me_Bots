# Multi-Tenancy Implementation Guide

## Overview

Multi-tenancy is the core architectural principle of this SaaS schema. Every major entity is linked to a `tenant_id`, ensuring complete data isolation between customers.

## Tenant Model

```python
# schemas/tenants.py
class Tenant(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(..., description="Organization name")
    api_key: str = Field(default_factory=lambda: uuid.uuid4().hex)
    is_active: bool = Field(default=True)

    # Subscription details
    subscription_id: Optional[uuid.UUID] = None
    current_plan_id: Optional[uuid.UUID] = None

    # Limits and quotas
    max_groups: int = Field(default=10)
    max_users_per_group: int = Field(default=100)
    ai_credits_per_month: int = Field(default=1000)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Tenant Resolution

### API Key Resolution
```python
# middleware.py
from fastapi import Request, HTTPException
from schemas.tenants import Tenant

async def get_tenant_from_api_key(request: Request) -> Tenant:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Query tenant by API key
    tenant = db.query(TenantTable).filter(
        TenantTable.api_key == api_key,
        TenantTable.is_active == True
    ).first()

    if not tenant:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return Tenant(**tenant.__dict__)
```

### Dependency Injection
```python
# main.py
from fastapi import Depends

@app.get("/users/", response_model=List[User])
async def get_users(tenant: Tenant = Depends(get_tenant_from_api_key)):
    # All queries automatically filtered by tenant_id
    users = db.query(UserTable).filter(
        UserTable.tenant_id == tenant.id
    ).all()

    return [User(**user.__dict__) for user in users]
```

## Data Isolation Patterns

### 1. Query Filtering
```python
# Always include tenant_id in WHERE clauses
def get_user_interactions(tenant_id: uuid.UUID, days: int = 30):
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    return db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= cutoff_date
    ).all()
```

### 2. Foreign Key Relationships
```python
# All relationships include tenant_id
class Group(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(...)  # Required foreign key
    groupme_group_id: str = Field(...)

class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(...)  # Required foreign key
    groupme_user_id: str = Field(...)
```

### 3. Database Constraints
```sql
-- Ensure data integrity at database level
ALTER TABLE users ADD CONSTRAINT fk_users_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);

ALTER TABLE groups ADD CONSTRAINT fk_groups_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);

-- Unique constraints per tenant
CREATE UNIQUE INDEX idx_groups_tenant_groupme_id
    ON groups(tenant_id, groupme_group_id);
```

## Usage Examples

### Creating Tenant-Scoped Resources
```python
@app.post("/groups/", response_model=Group)
async def create_group(
    group_data: GroupCreate,
    tenant: Tenant = Depends(get_tenant_from_api_key)
):
    # Automatically set tenant_id
    group = Group(
        **group_data.dict(),
        tenant_id=tenant.id
    )

    # Validate against tenant limits
    existing_groups = db.query(GroupTable).filter(
        GroupTable.tenant_id == tenant.id
    ).count()

    if existing_groups >= tenant.max_groups:
        raise HTTPException(status_code=400, detail="Group limit exceeded")

    # Save to database
    return group
```

### Cross-Tenant Analytics
```python
@app.get("/analytics/summary")
async def get_analytics_summary(
    tenant: Tenant = Depends(get_tenant_from_api_key)
):
    # Aggregate data for this tenant only
    total_users = db.query(UserTable).filter(
        UserTable.tenant_id == tenant.id
    ).count()

    total_interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant.id
    ).count()

    return {
        "total_users": total_users,
        "total_interactions": total_interactions,
        "plan_limits": {
            "max_groups": tenant.max_groups,
            "ai_credits_used": get_ai_credits_used(tenant.id)
        }
    }
```

## Best Practices

### 1. Consistent Tenant Context
- Always pass `tenant_id` as the first parameter in queries
- Use dependency injection to ensure tenant context in all endpoints
- Validate tenant limits before creating resources

### 2. API Key Security
- Generate unique API keys for each tenant
- Implement rate limiting per API key
- Rotate API keys periodically

### 3. Data Migration
```python
# When migrating data between tenants
def migrate_user_to_tenant(user_id: uuid.UUID, new_tenant_id: uuid.UUID):
    # Update all related records
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    user.tenant_id = new_tenant_id

    # Update related interactions
    db.query(BotInteractionTable).filter(
        BotInteractionTable.user_id == user_id
    ).update({"tenant_id": new_tenant_id})

    db.commit()
```

### 4. Testing Multi-Tenancy
```python
# Test data isolation
def test_tenant_isolation():
    tenant1 = create_test_tenant("Company A")
    tenant2 = create_test_tenant("Company B")

    # Create users for each tenant
    user1 = create_user(tenant1.id, "user1")
    user2 = create_user(tenant2.id, "user2")

    # Verify isolation
    tenant1_users = get_users_for_tenant(tenant1.id)
    tenant2_users = get_users_for_tenant(tenant2.id)

    assert user1 in tenant1_users
    assert user2 in tenant2_users
    assert user1 not in tenant2_users
    assert user2 not in tenant1_users
```

## Troubleshooting

### Common Issues

1. **Missing tenant_id in queries**
   - Always include `tenant_id` filter in WHERE clauses
   - Use database constraints to prevent orphaned records

2. **API key not found**
   - Verify API key format and tenant activation status
   - Check database indexes on api_key field

3. **Tenant limit exceeded**
   - Implement proper validation in create endpoints
   - Consider soft limits with upgrade prompts

4. **Data leaks between tenants**
   - Audit all queries for proper tenant filtering
   - Use database-level constraints where possible

## Next Steps

- [Model Relationships](./03_model_relationships.md) - Understanding entity relationships
- [Analytics Implementation](./04_analytics_and_optimization.md) - Performance tracking
- [Monetization Strategies](./05_monetization_strategies.md) - Revenue optimization
