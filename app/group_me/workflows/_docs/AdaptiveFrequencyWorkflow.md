# AdaptiveFrequencyWorkflow

## Overview
The AdaptiveFrequencyWorkflow intelligently controls outbound message cadence based on user engagement patterns and group activity levels. This ensures optimal communication timing without overwhelming users.

## Purpose
- **Primary Goal**: Maintain adaptive send frequency to improve engagement by 20%
- **Secondary Goals**: Prevent message fatigue, optimize response rates, respect user preferences

## Key Features

### Engagement Analysis
- Monitors user response patterns and activity levels
- Tracks optimal communication windows per user/group
- Identifies engagement peaks and valleys

### Frequency Optimization
- Dynamically adjusts message frequency based on real-time data
- Implements burst mode for high-engagement scenarios
- Respects user-defined frequency preferences

### Performance Tracking
- Measures frequency alignment with user behavior
- Tracks burst mode activation and effectiveness
- Monitors overall engagement impact

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group for frequency analysis |
| `content_type` | string | "general" | Type of content being sent |
| `target_frequency` | float | 1.0 | Desired messages per hour |
| `chat_window_hours` | integer | 24 | Analysis window in hours |
| `conversation_limit` | integer | 10 | Maximum conversations to analyze |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["adaptive_frequency_control"]
result = await workflow.execute(context,
    group_id="group_123",
    target_frequency=2.0,
    chat_window_hours=48
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `frequency_alignment` | >=90% | Messages within adaptive band |
| `burst_mode_latency` | <5m | Reaction time to burst activations |

## Related Workflows
- **PersonalizationEngineWorkflow**: Customizes frequency per user preferences
- **ABTestingWorkflow**: Tests optimal frequency settings
