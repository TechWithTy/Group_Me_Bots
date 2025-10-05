# CommunityHealthMonitoringWorkflow

## Overview
The CommunityHealthMonitoringWorkflow tracks overall community sentiment, toxicity levels, and engagement patterns to maintain a positive and healthy community environment.

## Purpose
- **Primary Goal**: Maintain community health score above 80% and detect toxicity within 10 minutes
- **Secondary Goals**: Foster positive interactions, prevent harassment, ensure inclusivity

## Key Features

### Sentiment Analysis
- Real-time sentiment tracking across all messages
- Trend analysis for community mood patterns
- Positive/negative interaction identification

### Toxicity Detection
- Advanced toxicity and harassment detection
- Automated moderation trigger system
- Community guideline violation flagging

### Engagement Monitoring
- Participation pattern analysis and diversity tracking
- User interaction quality assessment
- Community growth and retention correlation

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group for monitoring |
| `minimum_health_score` | float | 0.8 | Minimum acceptable health score |
| `max_toxicity_threshold` | float | 0.1 | Maximum toxicity rate |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["community_health_sentiment_monitoring"]
result = await workflow.execute(context,
    group_id="group_123",
    minimum_health_score=0.75
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `community_health_score` | >=80% | Overall community health rating |
| `toxicity_detection_rate` | >=90% | Toxicity incidents detected |
| `engagement_diversity` | >=70% | Diverse engagement patterns |

## Related Workflows
- **SecurityModerationWorkflow**: Handles detected violations
- **UserRetentionChurnPreventionWorkflow**: Addresses engagement issues
