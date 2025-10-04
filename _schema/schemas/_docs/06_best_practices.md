# Best Practices and Implementation Guide

## Overview

This guide provides best practices for implementing and maintaining the SaaS GroupMe bot schema effectively.

## 1. Schema Design Best Practices

### 1.1 Consistent Field Naming
```python
# ✅ Good: Consistent naming across models
class User(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class Group(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# ❌ Avoid: Inconsistent naming
class User(BaseModel):
    user_id: uuid.UUID
    tenant: uuid.UUID
    creation_time: datetime
    last_modified: datetime
```

### 1.2 Proper Foreign Key Relationships
```python
# ✅ Good: Clear foreign key relationships
class BotInteraction(BaseModel):
    id: str
    tenant_id: uuid.UUID
    user_id: uuid.UUID      # Links to User.id
    group_id: str          # Links to Group.id
    bot_id: str           # Links to ChatBot.id

# ❌ Avoid: Ambiguous relationships
class BotInteraction(BaseModel):
    id: str
    user: str             # Unclear what this links to
    group: str            # Could be name or ID
```

### 1.3 Flexible Metadata Fields
```python
# ✅ Good: Flexible configuration storage
class MonetizationSource(BaseModel):
    details: Dict[str, Any] = Field(default_factory=dict)
    # Can store custom configuration without schema changes

# ❌ Avoid: Rigid configuration
class MonetizationSource(BaseModel):
    api_endpoint: str
    api_key: str
    retry_count: int
    # Requires schema migration for new config options
```

## 2. Implementation Best Practices

### 2.1 Error Handling
```python
# ✅ Good: Comprehensive error handling
async def create_conversion_tracking(conversion_data: dict):
    try:
        # Validate input data
        conversion = ConversionTracking(**conversion_data)

        # Check foreign key relationships
        if not await interaction_exists(conversion.interaction_id):
            raise ValueError("Invalid interaction_id")

        # Save to database
        db.add(conversion)
        db.commit()

        return conversion

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid conversion data")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

# ❌ Avoid: Minimal error handling
async def create_conversion_tracking(conversion_data: dict):
    conversion = ConversionTracking(**conversion_data)
    db.add(conversion)
    db.commit()
    return conversion
```

### 2.2 Database Optimization
```python
# ✅ Good: Optimized queries with proper indexing
def get_tenant_analytics(tenant_id: uuid.UUID, start_date: datetime):
    return db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= start_date
    ).options(
        selectinload(BotInteractionTable.conversions)
    ).all()

# Create appropriate indexes
CREATE INDEX idx_bot_interactions_tenant_date
ON bot_interactions(tenant_id, created_at DESC);

# ❌ Avoid: Inefficient queries
def get_tenant_analytics(tenant_id: uuid.UUID, start_date: datetime):
    # N+1 query problem
    interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= start_date
    ).all()

    # Separate query for each interaction
    for interaction in interactions:
        conversions = db.query(ConversionTrackingTable).filter(
            ConversionTrackingTable.interaction_id == interaction.id
        ).all()

    return interactions
```

### 2.3 API Design
```python
# ✅ Good: RESTful API design
@app.get("/tenants/{tenant_id}/analytics")
async def get_tenant_analytics(
    tenant_id: uuid.UUID,
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    tenant: Tenant = Depends(get_tenant_from_api_key)
):
    # Validate tenant access
    if tenant.id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Use query parameters for filtering
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date

    return get_tenant_analytics_data(tenant_id, **filters)

# ❌ Avoid: Poor API design
@app.get("/analytics")
async def get_analytics(tenant_id: str, start_date: str, end_date: str):
    # String parameters instead of proper types
    # No tenant validation
    # Poor parameter naming
    pass
```

## 3. Performance Best Practices

### 3.1 Asynchronous Operations
```python
# ✅ Good: Async database operations
async def bulk_insert_interactions(interactions: List[BotInteraction]):
    async with db.begin():
        db.add_all(interactions)
        await db.commit()

# ✅ Good: Async analytics processing
async def process_analytics_batch(tenant_id: uuid.UUID):
    # Process analytics in background
    analytics_data = await gather_analytics_data(tenant_id)

    # Update aggregated KPIs
    await update_kpi_aggregates(tenant_id, analytics_data)

# ❌ Avoid: Blocking operations
def process_analytics_batch(tenant_id: uuid.UUID):
    # Blocks the event loop
    time.sleep(5)
    return analytics_data
```

### 3.2 Caching Strategy
```python
# ✅ Good: Intelligent caching
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_tenant_settings(tenant_id: uuid.UUID):
    # Cache for 1 hour
    cache_key = f"tenant_settings:{tenant_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    settings = db.query(TenantSettingsTable).filter(
        TenantSettingsTable.tenant_id == tenant_id
    ).first()

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(settings.__dict__))
    return settings

# ❌ Avoid: No caching
def get_tenant_settings(tenant_id: uuid.UUID):
    # Database query on every call
    return db.query(TenantSettingsTable).filter(
        TenantSettingsTable.tenant_id == tenant_id
    ).first()
```

## 4. Security Best Practices

### 4.1 Input Validation
```python
# ✅ Good: Comprehensive validation
class CreateTenantRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=32, max_length=64)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('api_key')
    def validate_api_key(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('API key contains invalid characters')
        return v

# ❌ Avoid: Minimal validation
class CreateTenantRequest(BaseModel):
    name: str
    api_key: str
```

### 4.2 API Key Security
```python
# ✅ Good: Secure API key handling
def generate_secure_api_key():
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str):
    return hashlib.sha256(api_key.encode()).hexdigest()

# Store hashed version only
tenant = Tenant(
    name="Customer Corp",
    api_key_hash=hash_api_key("user_provided_key")
)

# Verify API key
def verify_api_key(provided_key: str, stored_hash: str):
    return hash_api_key(provided_key) == stored_hash

# ❌ Avoid: Plain text storage
tenant = Tenant(
    api_key="plaintext_key_123"  # Security risk!
)
```

## 5. Testing Best Practices

### 5.1 Comprehensive Test Coverage
```python
# ✅ Good: Test all scenarios
def test_tenant_creation():
    tenant_data = {
        "name": "Test Tenant",
        "api_key": "test-key-123"
    }

    # Test successful creation
    tenant = create_tenant(tenant_data)
    assert tenant.name == "Test Tenant"
    assert tenant.api_key == "test-key-123"

    # Test validation errors
    with pytest.raises(ValidationError):
        create_tenant({"name": ""})  # Empty name

    # Test duplicate constraints
    with pytest.raises(IntegrityError):
        create_tenant(tenant_data)  # Duplicate API key

# ❌ Avoid: Incomplete testing
def test_tenant_creation():
    tenant = create_tenant({"name": "Test"})
    assert tenant.name == "Test"
    # Missing edge cases and error scenarios
```

### 5.2 Database Testing
```python
# ✅ Good: Proper database testing
@pytest.fixture
def db_session():
    # Create test database
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()

def test_conversion_tracking(db_session):
    # Create test data
    tenant = Tenant(name="Test", api_key="test")
    db_session.add(tenant)
    db_session.commit()

    interaction = BotInteraction(
        tenant_id=tenant.id,
        message_text="Test message"
    )
    db_session.add(interaction)
    db_session.commit()

    # Test conversion tracking
    conversion = ConversionTracking(
        tenant_id=tenant.id,
        interaction_id=interaction.id,
        outcome="purchased"
    )

    db_session.add(conversion)
    db_session.commit()

    # Verify data integrity
    saved_conversion = db_session.query(ConversionTrackingTable).first()
    assert saved_conversion.outcome == "purchased"
```

## 6. Monitoring and Logging Best Practices

### 6.1 Structured Logging
```python
# ✅ Good: Structured logging
import logging
import json

logger = logging.getLogger(__name__)

def log_bot_interaction(interaction: BotInteraction):
    logger.info("Bot interaction processed", extra={
        "tenant_id": str(interaction.tenant_id),
        "interaction_id": interaction.id,
        "intent": interaction.intent,
        "sentiment": interaction.sentiment,
        "response_time_ms": interaction.response_time_ms
    })

# ❌ Avoid: Unstructured logging
def log_bot_interaction(interaction: BotInteraction):
    logger.info(f"Processed interaction for tenant {interaction.tenant_id}")
```

### 6.2 Performance Monitoring
```python
# ✅ Good: Performance monitoring
from time import time
import prometheus_client as prom

# Metrics
interaction_count = prom.Counter('bot_interactions_total', 'Total bot interactions', ['tenant_id', 'bot_id'])
response_time_histogram = prom.Histogram('bot_response_time_seconds', 'Bot response time')

async def handle_message(message_data: dict):
    start_time = time()

    try:
        # Process message
        result = await process_message(message_data)

        # Record metrics
        interaction_count.labels(
            tenant_id=str(message_data["tenant_id"]),
            bot_id=message_data["bot_id"]
        ).inc()

        response_time = time() - start_time
        response_time_histogram.observe(response_time)

        return result

    except Exception as e:
        logger.error("Message processing failed", extra={
            "error": str(e),
            "tenant_id": message_data["tenant_id"]
        })
        raise
```

## 7. Deployment Best Practices

### 7.1 Environment Configuration
```python
# ✅ Good: Environment-based configuration
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    debug: bool = False
    log_level: str = "INFO"

    # Environment-specific settings
    if os.getenv("ENVIRONMENT") == "production":
        workers: int = 4
        cache_ttl: int = 3600
    else:
        workers: int = 1
        cache_ttl: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

# ❌ Avoid: Hard-coded configuration
DATABASE_URL = "postgresql://localhost/mydb"
DEBUG = True
```

### 7.2 Health Checks
```python
# ✅ Good: Comprehensive health checks
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "bot_services": await check_bot_status()
    }

    # Determine overall status
    if all(status == "ok" for status in health_status.values()):
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

async def check_database_connection():
    try:
        db.execute("SELECT 1")
        return "ok"
    except Exception:
        return "error"

# ❌ Avoid: No health checks
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## 8. Maintenance Best Practices

### 8.1 Data Migration
```python
# ✅ Good: Safe data migration
def migrate_add_engagement_score():
    # Add new column
    with db.begin():
        db.execute("ALTER TABLE group_members ADD COLUMN engagement_score FLOAT DEFAULT 0")

    # Populate with calculated values
    members = db.query(GroupMemberTable).all()
    for member in members:
        member.engagement_score = calculate_engagement_score(member)
        db.add(member)

    db.commit()

# ❌ Avoid: Risky migration
def migrate_add_engagement_score():
    db.execute("ALTER TABLE group_members ADD COLUMN engagement_score FLOAT")
    # No data population or error handling
```

### 8.2 Backup and Recovery
```python
# ✅ Good: Automated backups
def create_database_backup(tenant_id: uuid.UUID):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"tenant_{tenant_id}_backup_{timestamp}.sql"

    # Export tenant data
    with open(backup_filename, 'w') as f:
        # Use pg_dump or similar for PostgreSQL
        subprocess.run([
            "pg_dump",
            "--data-only",
            f"--where=tenant_id={tenant_id}",
            os.getenv("DATABASE_URL"),
        ], stdout=f)

    return backup_filename

# ❌ Avoid: Manual backup process
def create_database_backup():
    # Manual process prone to errors
    pass
```

## 9. Documentation Best Practices

### 9.1 API Documentation
```python
# ✅ Good: Comprehensive API docs
@app.post("/conversions/", response_model=ConversionTracking)
async def create_conversion(
    conversion: ConversionTracking,
    tenant: Tenant = Depends(get_tenant_from_api_key)
):
    """
    Create a conversion tracking record.

    This endpoint tracks bot-initiated conversions including:
    - Checkout completions
    - User purchases
    - Sign-ups and other conversions

    **Parameters:**
    - **conversion**: ConversionTracking model with all required fields

    **Returns:**
    - Created ConversionTracking record

    **Errors:**
    - 400: Invalid conversion data
    - 403: Tenant access denied
    - 404: Referenced interaction not found
    """
    pass
```

### 9.2 Code Documentation
```python
# ✅ Good: Comprehensive code documentation
def calculate_conversion_rate(
    interactions: List[BotInteraction],
    conversions: List[ConversionTracking]
) -> float:
    """
    Calculate conversion rate for a set of interactions.

    Args:
        interactions: List of bot interactions
        conversions: List of conversion tracking records

    Returns:
        Conversion rate as a float (0.0 to 1.0)

    Raises:
        ValueError: If no interactions provided

    Example:
        >>> interactions = [BotInteraction(...)]
        >>> conversions = [ConversionTracking(...)]
        >>> rate = calculate_conversion_rate(interactions, conversions)
        >>> print(f"Conversion rate: {rate:.2%}")
    """
    if not interactions:
        raise ValueError("No interactions provided")

    successful_conversions = sum(
        1 for c in conversions
        if c.outcome == "purchased"
    )

    return successful_conversions / len(interactions)
```

## Summary

Following these best practices ensures:
- **Maintainable Code**: Consistent patterns and proper error handling
- **Scalable Architecture**: Optimized queries and caching strategies
- **Security**: Proper input validation and secure API key handling
- **Reliability**: Comprehensive testing and monitoring
- **Performance**: Efficient database operations and async processing

## Next Steps

- Review the [API Reference](../../api/) for endpoint documentation
- Check the [Deployment Guide](../../deployment/) for production setup
- Explore [Troubleshooting](../../troubleshooting/) for common issues

## Support

For questions or issues:
- Check the [FAQ](../../faq/) first
- Open an issue on [GitHub](https://github.com/your-repo/issues)
- Contact support at support@yourcompany.com
