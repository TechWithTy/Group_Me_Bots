# ABTestingWorkflow

## Overview
The ABTestingWorkflow enables controlled experiments on features like message frequency, content types, or UI elements to measure impact and optimize user experience.

## Purpose
- **Primary Goal**: Run A/B tests on engagement features and achieve statistical significance in 80% of experiments
- **Secondary Goals**: Validate feature effectiveness, optimize user experience, reduce guesswork

## Key Features

### Experiment Design
- Statistical test setup and configuration
- Variant creation and management
- Sample size calculation and validation

### Execution Management
- Automated test execution and monitoring
- Real-time metrics collection and analysis
- Early stopping rules for conclusive results

### Results Analysis
- Statistical significance testing
- Confidence interval calculation
- Practical significance assessment

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `test_name` | string | "default_test" | Name of the experiment |
| `variant_a_users` | integer | 50 | Users in control group |
| `variant_b_users` | integer | 50 | Users in treatment group |
| `minimum_sample_size` | integer | 100 | Minimum total participants |

## Usage Example

```python
workflow = WORKFLOW_REGISTRY["ab_testing_experiments"]
result = await workflow.execute(context,
    test_name="frequency_optimization_test",
    variant_a_users=100,
    variant_b_users=100,
    minimum_sample_size=200
)
```

## KPIs Tracked

| KPI | Target | Description |
|-----|--------|-------------|
| `test_completion_rate` | >=80% | Experiments reaching significance |
| `sample_size_adequacy` | >=100 | Minimum participants per variant |

## Related Workflows
- **AdaptiveFrequencyWorkflow**: Tests frequency optimization strategies
- **PersonalizationEngineWorkflow**: Validates personalization effectiveness
