# OnboardingFunnelWorkflow

## Overview
The OnboardingFunnelWorkflow guides new members through structured onboarding touch-points to ensure successful community integration and long-term engagement.

## Purpose
- **Primary Goal**: Deliver onboarding nudges to 90% of new members within 24 hours
- **Secondary Goals**: Increase retention rates, improve user experience, reduce support tickets

## Key Features

### Automated Welcome
- Instant welcome message delivery
- Personalized onboarding content
- Progress tracking and milestone celebration

### Touch-point Management
- Sequential onboarding step execution
- Adaptive content based on user responses
- Skip logic for advanced users

### Progress Monitoring
- Completion rate tracking and analysis
- Dropout point identification
- Success correlation with engagement metrics

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group for onboarding |
| `user_ids` | list[string] | Required | New users to onboard |
| `minimum_users` | integer | 1 | Minimum users threshold |
| `welcome_message` | string | Required | Welcome message template |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["onboarding_funnel_automation"]
result = await workflow.execute(context,
    group_id="group_123",
    user_ids=["user_1", "user_2", "user_3"],
    welcome_message="Welcome! Check pinned posts for starter info."
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `nudge_coverage` | >=90% | Fraction of new users nudged |
| `follow_up_completion` | >=70% | Users completing onboarding |

## Related Workflows
- **UserRetentionChurnPreventionWorkflow**: Monitors onboarding success impact
- **PersonalizationEngineWorkflow**: Customizes onboarding experience
