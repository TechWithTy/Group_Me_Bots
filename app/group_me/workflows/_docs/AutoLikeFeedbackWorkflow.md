# AutoLikeFeedbackWorkflow

## Overview
The AutoLikeFeedbackWorkflow closes the feedback loop by automatically reacting to high-value messages with bot acknowledgments. This encourages continued community participation and signals content appreciation.

## Purpose
- **Primary Goal**: Acknowledge 100% of priority messages with bot reactions
- **Secondary Goals**: Encourage content creation, build community rapport, track engagement signals

## Key Features

### Message Detection
- Identifies high-value messages based on content quality and context
- Prioritizes messages requiring acknowledgment
- Filters spam and low-quality content

### Automated Responses
- Generates contextual reactions and feedback messages
- Customizes response tone and style per community
- Includes tracking hashtags for analytics

### Engagement Tracking
- Monitors response effectiveness and user reactions
- Tracks feedback loop completion rates
- Measures community response to bot interactions

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group for feedback |
| `message_ids` | list[string] | Required | Messages to acknowledge |
| `reaction_text` | string | "👍" | Reaction emoji/text |
| `feedback_suffix` | string | "#CommunityBoost" | Tracking hashtag |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["auto_like_feedback_loop"]
result = await workflow.execute(context,
    group_id="group_123",
    message_ids=["msg_1", "msg_2", "msg_3"],
    reaction_text="🚀",
    feedback_suffix="#AwesomeContent"
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `reaction_coverage` | 100% | Messages receiving auto-like |
| `feedback_latency` | <30s | Time to react after detection |

## Related Workflows
- **MessageStitchingWorkflow**: Uses engagement signals for content selection
- **ContentQualityRelevanceWorkflow**: Ensures reaction-worthy content
