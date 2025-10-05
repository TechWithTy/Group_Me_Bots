# ContentQualityRelevanceWorkflow

## Overview
The ContentQualityRelevanceWorkflow ensures all content meets established quality standards and aligns with user interests and community guidelines. This maintains content value and user satisfaction.

## Purpose
- **Primary Goal**: Maintain 90% content relevance score and minimize quality violations
- **Secondary Goals**: Improve user experience, increase content engagement, ensure brand consistency

## Key Features

### Content Evaluation
- Analyzes message relevance to community interests
- Assesses content quality against established criteria
- Identifies potential policy violations or spam

### Quality Scoring
- Multi-dimensional content quality assessment
- User satisfaction prediction and tracking
- Content improvement recommendations

### Violation Detection
- Automated quality threshold monitoring
- Content quarantine and review systems
- User feedback integration for scoring

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group for analysis |
| `limit` | integer | 20 | Messages to evaluate per run |
| `minimum_relevance_score` | float | 0.9 | Minimum acceptable relevance |
| `quality_threshold` | float | 0.8 | Quality score threshold |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["content_quality_relevance_assurance"]
result = await workflow.execute(context,
    group_id="group_123",
    minimum_relevance_score=0.85
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `content_relevance_score` | >=90% | Average relevance to user interests |
| `user_satisfaction_ratings` | >=4.0 | Average user satisfaction score |
| `quality_violation_rate` | <=5% | Rate of quality standard violations |

## Related Workflows
- **AutoLikeFeedbackWorkflow**: Provides user satisfaction signals
- **CommunityHealthMonitoringWorkflow**: Monitors content impact on community
