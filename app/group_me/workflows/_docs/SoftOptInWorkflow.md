# SoftOptInWorkflow

## Overview
The SoftOptInWorkflow identifies and enrolls users showing commercial interest through subtle engagement patterns and converts them into active subscribers.

## Purpose
- **Primary Goal**: Capture soft opt-in interest from at least 70% of engaged members
- **Secondary Goals**: Increase conversion rates, improve lead quality, respect user preferences

## Key Features

### Interest Detection
- Subtle commercial intent pattern recognition
- Engagement-based interest scoring
- Non-intrusive preference identification

### Opt-in Conversion
- Contextual opt-in opportunity presentation
- Frictionless conversion process
- Preference confirmation and validation

### Follow-up Management
- Automated follow-up message delivery
- Interest nurturing and relationship building
- Conversion tracking and optimization

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | dict | Required | User message with potential interest |
| `acceptance_target` | integer | 5 | Target opt-in conversions |
| `follow_up_text` | string | Required | Follow-up message template |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["soft_opt_in_capture"]
result = await workflow.execute(context,
    message={"user_id": "user_1", "text": "I'm interested in deals"},
    acceptance_target=3,
    follow_up_text="Thanks for your interest! Reply YES to receive deals."
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `soft_opt_in_rate` | >=70% | Users with soft opt-in state |
| `follow_up_latency` | <10m | Time to react to opt-in signal |

## Related Workflows
- **CommerceIntentWorkflow**: Identifies commercial opportunities
- **PersonalizationEngineWorkflow**: Customizes opt-in approaches
