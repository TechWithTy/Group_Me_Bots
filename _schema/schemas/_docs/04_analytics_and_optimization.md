# Analytics and Optimization Guide

## Overview

The analytics system provides comprehensive tracking and optimization capabilities for bot performance, user engagement, and business outcomes.

## Core Analytics Models

### 1. BotInteraction - Individual Interaction Tracking
```python
# schemas/analytics.py
class BotInteraction(BaseModel):
    id: str
    tenant_id: uuid.UUID

    timestamp: datetime
    group_id: str
    member_id: str
    bot_id: str

    message_text: str
    intent: str                    # AI-detected user intent
    sentiment: str                 # positive, neutral, negative
    monetization_event: bool       # Did this lead to revenue?

    response_text: Optional[str]
    response_time_ms: Optional[int]
```

### 2. ConversionTracking - Outcome Analysis
```python
class ConversionTracking(BaseModel):
    # Links to BotInteraction
    interaction_id: str
    trigger_message: str           # What the user said
    intent_score: float           # AI confidence (0-1)
    bot_message: str              # Bot's response

    # Outcome tracking
    outcome: str                  # purchased, visited, did_nothing
    conversion_value: float       # Revenue generated
    checkout_completed: bool      # Full funnel completion
```

### 3. BotPerformanceMetrics - KPI Tracking
```python
class BotPerformanceMetrics(BaseModel):
    metric_category: MetricCategory  # customer_experience, operational_efficiency, etc.
    metric_type: str                 # csat, containment_rate, etc.
    metric_value: float             # The actual metric value

    # Context
    aggregation_period: str         # hourly, daily, weekly, monthly
    sample_size: int               # Data points in aggregation
```

## Analytics Implementation

### 1. Setting Up Analytics Collection
```python
# In your bot handler
async def handle_message(message_data: dict):
    # Extract context
    tenant_id = get_tenant_id_from_api_key(message_data["api_key"])
    user_id = message_data["user_id"]
    group_id = message_data["group_id"]
    bot_id = message_data["bot_id"]

    # Create interaction record
    interaction = BotInteraction(
        tenant_id=tenant_id,
        group_id=group_id,
        member_id=user_id,
        bot_id=bot_id,
        message_text=message_data["text"],
        intent=detect_intent(message_data["text"]),
        sentiment=analyze_sentiment(message_data["text"])
    )

    # Save to database
    db.add(interaction)
    db.commit()

    # Process message and generate response
    response = generate_bot_response(interaction)

    # Update interaction with response
    interaction.response_text = response
    interaction.response_time_ms = calculate_response_time()
    db.commit()

    return response
```

### 2. Tracking Conversions
```python
# In your e-commerce integration
async def track_conversion(interaction_id: str, conversion_data: dict):
    conversion = ConversionTracking(
        interaction_id=interaction_id,
        trigger_message=conversion_data["trigger"],
        intent_score=conversion_data["intent_confidence"],
        bot_message=conversion_data["bot_response"],
        outcome=conversion_data["outcome"],
        conversion_value=conversion_data.get("value", 0),
        checkout_completed=conversion_data["completed"],
        pages_visited=conversion_data["journey"],
        time_to_conversion_seconds=conversion_data["time_taken"]
    )

    db.add(conversion)
    db.commit()

    # Also log monetization event if revenue generated
    if conversion.conversion_value > 0:
        monetization_event = MonetizationEventLog(
            tenant_id=conversion.tenant_id,
            interaction_id=interaction_id,
            revenue_generated=conversion.conversion_value,
            event_details={"conversion_type": conversion.conversion_type}
        )
        db.add(monetization_event)
        db.commit()
```

## Optimization Strategies

### 1. Using the BotOptimizer Engine
```python
# bot_optimization.py
from schemas.bot_optimization import BotOptimizer

# Initialize optimizer
optimizer = BotOptimizer(db_session)

# Analyze monetization opportunities
monetization_insights = optimizer.analyze_monetization_triggers(tenant_id)
print(f"Top profitable intents: {monetization_insights.profitable_intents}")

# Generate personalization rules
personalization_rules = optimizer.generate_personalization_rules(tenant_id)
print(f"Upsell opportunities: {personalization_rules.upsell_opportunities}")

# Get optimization recommendations
recommendations = optimizer.generate_optimization_recommendations(tenant_id)
for rec in recommendations:
    print(f"Priority: {rec.implementation_priority} - {rec.impact_estimate}")
```

### 2. Sentiment-Based Optimization
```python
# Analyze sentiment for engagement strategies
sentiment_opt = optimizer.optimize_sentiment_engagement(tenant_id)

# Use in bot responses
def generate_empathetic_response(user_message: str, sentiment: str):
    if sentiment == "negative":
        # Use de-escalation triggers
        if any(keyword in user_message.lower() for keyword in sentiment_opt.de_escalation_triggers):
            return "I understand this is frustrating. Let me help you resolve this issue."

    elif sentiment == "positive":
        # Reinforce positive sentiment
        return choice(sentiment_opt.positive_reinforcement_responses)

    return "How can I assist you today?"
```

### 3. Personalization Implementation
```python
# Use personalization rules in responses
def personalize_response(user_id: uuid.UUID, message: str):
    user_segment = get_user_segment(user_id)

    if user_segment == "paid_subscriber":
        # Offer premium features
        return "As a valued subscriber, you have access to advanced features. Would you like to explore them?"

    elif user_segment == "free_user":
        # Highlight upgrade benefits
        return "Upgrade to premium for unlimited access to these features!"

    return generate_standard_response(message)
```

## KPI Dashboards

### 1. Customer Experience Metrics
```python
def get_customer_experience_kpis(tenant_id: uuid.UUID, days: int = 30):
    # CSAT Score
    feedback = db.query(CustomerFeedbackTable).filter(
        CustomerFeedbackTable.tenant_id == tenant_id,
        CustomerFeedbackTable.created_at >= datetime.utcnow() - timedelta(days=days)
    ).all()

    avg_csat = sum(f.csat_rating for f in feedback if f.csat_rating) / len([f for f in feedback if f.csat_rating])

    # Sentiment Analysis
    interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.sentiment.isnot(None)
    ).all()

    sentiment_dist = Counter(i.sentiment for i in interactions)

    return {
        "avg_csat": avg_csat,
        "sentiment_distribution": dict(sentiment_dist),
        "positive_sentiment_rate": sentiment_dist.get("positive", 0) / len(interactions)
    }
```

### 2. Operational Efficiency Metrics
```python
def get_operational_kpis(tenant_id: uuid.UUID, days: int = 30):
    interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= datetime.utcnow() - timedelta(days=days)
    ).all()

    conversions = db.query(ConversionTrackingTable).filter(
        ConversionTrackingTable.tenant_id == tenant_id,
        ConversionTrackingTable.created_at >= datetime.utcnow() - timedelta(days=days)
    ).all()

    # Containment Rate
    escalated = sum(1 for i in interactions if i.intent == "escalate")
    containment_rate = 1 - (escalated / len(interactions)) if interactions else 0

    # Resolution Rate
    resolved = sum(1 for c in conversions if c.outcome in ["purchased", "resolved"])
    resolution_rate = resolved / len(interactions) if interactions else 0

    # Average Handling Time
    response_times = [i.response_time_ms for i in interactions if i.response_time_ms]
    avg_handling_time = sum(response_times) / len(response_times) if response_times else 0

    return {
        "containment_rate": containment_rate,
        "resolution_rate": resolution_rate,
        "avg_handling_time_ms": avg_handling_time,
        "total_conversions": len(conversions)
    }
```

### 3. Engagement Metrics
```python
def get_engagement_kpis(tenant_id: uuid.UUID, days: int = 30):
    members = db.query(GroupMemberTable).filter(
        GroupMemberTable.tenant_id == tenant_id,
        GroupMemberTable.last_activity >= datetime.utcnow() - timedelta(days=days)
    ).all()

    interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= datetime.utcnow() - timedelta(days=days)
    ).all()

    # Active Users & Retention
    active_users = len(set(m.user_id for m in members if m.user_id))
    total_users = db.query(UserTable).filter(UserTable.tenant_id == tenant_id).count()
    retention_rate = active_users / total_users if total_users > 0 else 0

    # Conversation Completion Rate
    completed_convos = sum(1 for i in interactions if i.intent not in ["abandoned", "fallback"])
    completion_rate = completed_convos / len(interactions) if interactions else 0

    # Bounce Rate
    single_message_sessions = sum(1 for i in interactions if not i.response_text)
    bounce_rate = single_message_sessions / len(interactions) if interactions else 0

    return {
        "active_users": active_users,
        "retention_rate": retention_rate,
        "completion_rate": completion_rate,
        "bounce_rate": bounce_rate,
        "total_interactions": len(interactions)
    }
```

## A/B Testing Implementation

### 1. Setting Up A/B Tests
```python
# Using the BotOptimizer
test_config = {
    "name": "Premium Feature Pitch",
    "type": "monetization_strategy",
    "control": {
        "response_template": "Our premium plan offers advanced features for $29/month."
    },
    "variant": {
        "response_template": "Unlock premium features and save 20% - only $23.20/month!"
    }
}

test_id = optimizer.run_ab_test(tenant_id, test_config)
```

### 2. Analyzing Test Results
```python
def analyze_ab_test(test_id: str):
    test_results = db.query(ABTestResultTable).filter(
        ABTestResultTable.id == test_id
    ).first()

    if not test_results:
        return {"error": "Test not found"}

    # Calculate conversion rates
    control_rate = test_results.control_conversions / test_results.control_sample_size
    variant_rate = test_results.variant_conversions / test_results.variant_sample_size

    # Statistical significance (simplified)
    improvement = (variant_rate - control_rate) / control_rate if control_rate > 0 else 0

    return {
        "control_rate": control_rate,
        "variant_rate": variant_rate,
        "improvement": improvement,
        "winner": test_results.winner,
        "recommended_action": test_results.recommended_action
    }
```

## Real-Time Analytics

### 1. Streaming Analytics
```python
# For real-time dashboards
def get_real_time_metrics(tenant_id: uuid.UUID):
    # Last hour metrics
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    recent_interactions = db.query(BotInteractionTable).filter(
        BotInteractionTable.tenant_id == tenant_id,
        BotInteractionTable.created_at >= one_hour_ago
    ).all()

    recent_conversions = db.query(ConversionTrackingTable).filter(
        ConversionTrackingTable.tenant_id == tenant_id,
        ConversionTrackingTable.created_at >= one_hour_ago
    ).all()

    return {
        "interactions_per_minute": len(recent_interactions) / 60,
        "conversion_rate": len([c for c in recent_conversions if c.outcome == "purchased"]) / len(recent_interactions) if recent_interactions else 0,
        "avg_response_time": sum(i.response_time_ms for i in recent_interactions if i.response_time_ms) / len([i for i in recent_interactions if i.response_time_ms]) if recent_interactions else 0
    }
```

## Performance Monitoring

### 1. Bot Health Checks
```python
def check_bot_health(bot_id: str, tenant_id: uuid.UUID):
    # Get recent performance metrics
    metrics = db.query(BotPerformanceMetricsTable).filter(
        BotPerformanceMetricsTable.bot_id == bot_id,
        BotPerformanceMetricsTable.tenant_id == tenant_id,
        BotPerformanceMetricsTable.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).all()

    if not metrics:
        return {"status": "insufficient_data"}

    # Check key metrics
    error_rate = next((m.metric_value for m in metrics if m.metric_type == "error_rate"), 0)
    avg_latency = next((m.metric_value for m in metrics if m.metric_type == "latency"), 0)

    health_score = 100
    if error_rate > 0.05:  # 5% error rate threshold
        health_score -= 30
    if avg_latency > 2000:  # 2 second latency threshold
        health_score -= 20

    return {
        "bot_id": bot_id,
        "health_score": health_score,
        "error_rate": error_rate,
        "avg_latency_ms": avg_latency,
        "recommendations": generate_health_recommendations(metrics)
    }
```

## Best Practices

### 1. Data Collection
- Collect analytics data asynchronously to avoid blocking bot responses
- Implement proper error handling for analytics failures
- Use batching for high-volume data insertion

### 2. Performance Optimization
- Create appropriate database indexes for analytics queries
- Use read replicas for complex reporting queries
- Implement caching for frequently accessed metrics

### 3. Privacy and Compliance
- Ensure all analytics data respects user privacy settings
- Implement data retention policies
- Provide opt-out mechanisms for analytics tracking

## Troubleshooting

### Common Issues

1. **Missing Analytics Data**
   - Check that analytics collection is properly integrated
   - Verify database connections and error handling

2. **Slow Analytics Queries**
   - Review index usage and add missing indexes
   - Consider query result caching

3. **Inaccurate Metrics**
   - Validate data collection points
   - Check for timezone and timestamp issues

## Next Steps

- [Monetization Strategies](./05_monetization_strategies.md) - Revenue optimization techniques
- [Best Practices](./06_best_practices.md) - Implementation guidelines
