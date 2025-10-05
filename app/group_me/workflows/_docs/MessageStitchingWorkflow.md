# MessageStitchingWorkflow

## Overview
The MessageStitchingWorkflow enables cross-group content sharing by identifying and echoing high-engagement messages across different communities. This workflow amplifies valuable content and increases overall community engagement.

## Purpose
- **Primary Goal**: Amplify cross-group engagement by echoing at least 5 high-signal messages per run
- **Secondary Goals**: Increase content visibility, foster community connections, identify trending topics

## Key Features

### Content Discovery
- Scans messages for engagement signals (reactions, replies, mentions)
- Identifies high-value content based on community response patterns
- Filters content by relevance and appropriateness

### Cross-Group Echoing
- Intelligently redistributes content across related groups
- Maintains content attribution and context
- Prevents content spam through rate limiting

### Engagement Amplification
- Tracks echo performance and community response
- Optimizes echo timing based on group activity patterns
- Measures cross-pollination success rates

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | string | Required | Target group ID for message scanning |
| `limit` | integer | 50 | Maximum messages to scan per execution |
| `target_echoes` | integer | 5 | Minimum messages to echo per run |

## Usage Example

```python
from app.group_me.workflows.workflow_suite import WORKFLOW_REGISTRY

workflow = WORKFLOW_REGISTRY["message_stitching_content_echo"]
result = await workflow.execute(context, group_id="group_123", limit=50, target_echoes=5)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `qualified_messages` | >=5 | Messages stitched across communities |
| `echo_success_rate` | >=0.8 | Share of qualifying messages echoed |

## Performance Metrics

- **Average Execution Time**: 2-5 seconds
- **Memory Usage**: ~50MB per 1000 messages processed
- **API Calls**: 1-2 per execution (depending on echo count)

## Related Workflows

- **AutoLikeFeedbackWorkflow**: Provides engagement signals for content selection
- **ContentQualityRelevanceWorkflow**: Ensures echoed content meets quality standards
- **CommunityHealthMonitoringWorkflow**: Monitors cross-group interaction patterns

## Best Practices

1. **Content Selection**: Focus on evergreen content that provides ongoing value
2. **Timing Optimization**: Schedule during peak community activity hours
3. **Rate Limiting**: Avoid overwhelming groups with too frequent echoes
4. **Attribution**: Always maintain original author credit and context

## Troubleshooting

### Common Issues

**Low Echo Count**
- Increase message scan limit
- Review content quality filters
- Check group activity levels

**Duplicate Content**
- Implement content hashing
- Add deduplication logic
- Monitor for spam patterns

**Performance Issues**
- Reduce batch sizes
- Add caching for repeated scans
- Optimize API rate limiting
