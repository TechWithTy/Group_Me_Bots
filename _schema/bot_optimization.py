from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from collections import Counter, defaultdict
from pydantic import BaseModel, Field
from dataclasses import dataclass

# Import models from analytics module
from .schemas.analytics import MonetizationEventLog, BotInteraction, BotPerformanceMetrics
from .schemas.users import GroupMember

class OptimizationRecommendation(BaseModel):
    """Stores AI-generated recommendations for bot improvements."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the recommendation")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    recommendation_type: str = Field(..., description="Type of optimization (monetization, sentiment, personalization, knowledge)")
    target_metric: str = Field(..., description="The metric being optimized (e.g., conversion_rate, engagement_score)")

    # Recommendation details
    current_value: float = Field(..., description="Current performance value")
    target_value: float = Field(..., description="Target performance value")
    confidence_score: float = Field(..., description="Confidence in the recommendation (0-1)")

    # Implementation details
    suggested_changes: Dict[str, Any] = Field(..., description="Specific changes to implement")
    implementation_priority: str = Field(default="medium", description="Priority level (low, medium, high, critical)")

    # Evidence
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Data that supports this recommendation")
    impact_estimate: str = Field(..., description="Estimated impact of implementing this change")

    # Status
    status: str = Field(default="pending", description="Status of the recommendation (pending, implemented, rejected)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    implemented_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ABTestResult(BaseModel):
    """Stores results of A/B tests for monetization strategies."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the A/B test")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    test_name: str = Field(..., description="Name of the A/B test")
    test_type: str = Field(..., description="Type of test (monetization_strategy, response_wording, etc.)")

    # Test variants
    control_group: Dict[str, Any] = Field(..., description="Control group configuration")
    variant_group: Dict[str, Any] = Field(..., description="Variant group configuration")

    # Results
    control_conversions: int = Field(default=0, description="Conversions in control group")
    variant_conversions: int = Field(default=0, description="Conversions in variant group")
    control_sample_size: int = Field(default=0, description="Sample size for control")
    variant_sample_size: int = Field(default=0, description="Sample size for variant")

    # Statistical significance
    p_value: Optional[float] = Field(None, description="Statistical significance")
    confidence_interval: Optional[Tuple[float, float]] = Field(None, description="Confidence interval for the effect")

    # Recommendation
    winner: str = Field(..., description="Which variant performed better (control, variant, inconclusive)")
    recommended_action: str = Field(..., description="Recommended next steps")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

@dataclass
class MonetizationInsights:
    """Insights from analyzing monetization triggers."""
    profitable_intents: List[Tuple[str, float]]  # (intent, conversion_rate)
    successful_patterns: List[Dict[str, Any]]  # Conversation patterns that convert
    drop_off_points: List[Dict[str, Any]]  # Where users disengage
    top_performing_responses: List[str]  # Response texts that drive conversions

@dataclass
class SentimentOptimization:
    """Recommendations for sentiment-based engagement."""
    de_escalation_triggers: List[str]  # Keywords that indicate frustration
    positive_reinforcement_responses: List[str]  # Responses that boost positive sentiment
    escalation_thresholds: Dict[str, float]  # When to escalate to human agent

@dataclass
class PersonalizationRules:
    """Rules for personalizing responses based on user data."""
    user_segment_rules: Dict[str, Dict[str, Any]]  # Rules for different user segments
    historical_preferences: Dict[str, List[str]]  # Past preferences per user
    upsell_opportunities: Dict[str, List[str]]  # Personalized upsell suggestions

@dataclass
class KnowledgeGapAnalysis:
    """Analysis of bot knowledge gaps and efficiency issues."""
    frequent_failures: List[Tuple[str, int]]  # (failed_query, frequency)
    long_conversation_paths: List[Dict[str, Any]]  # Conversation flows that are too long
    slow_response_patterns: List[Tuple[str, float]]  # (intent, avg_latency_ms)

class BotOptimizer:
    """Analytics engine for optimizing bot performance and monetization."""

    def __init__(self, db_session):
        self.db = db_session

    def analyze_monetization_triggers(self, tenant_id: uuid.UUID, days: int = 30) -> MonetizationInsights:
        """Analyze which interactions lead to monetization events."""
        # Query bot interactions and monetization events for the tenant
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get monetization events
        monetization_events = self.db.query(MonetizationEventLog).filter(
            MonetizationEventLog.tenant_id == tenant_id,
            MonetizationEventLog.created_at >= cutoff_date
        ).all()

        # Get corresponding bot interactions
        interaction_ids = [event.interaction_id for event in monetization_events]
        interactions = self.db.query(BotInteraction).filter(
            BotInteraction.id.in_(interaction_ids)
        ).all()

        # Analyze profitable intents
        intent_conversions = Counter()
        total_intents = Counter()

        for interaction in interactions:
            total_intents[interaction.intent] += 1
            if interaction.monetization_event:
                intent_conversions[interaction.intent] += 1

        profitable_intents = [
            (intent, intent_conversions[intent] / total_intents[intent])
            for intent in intent_conversions
            if total_intents[intent] > 10  # Minimum sample size
        ]
        profitable_intents.sort(key=lambda x: x[1], reverse=True)

        return MonetizationInsights(
            profitable_intents=profitable_intents[:10],  # Top 10
            successful_patterns=[],  # Would analyze conversation patterns
            drop_off_points=[],  # Would identify conversation drop-offs
            top_performing_responses=[]  # Would extract successful response texts
        )

    def optimize_sentiment_engagement(self, tenant_id: uuid.UUID) -> SentimentOptimization:
        """Analyze sentiment data for better engagement strategies."""
        # Query recent bot interactions with sentiment data
        interactions = self.db.query(BotInteraction).filter(
            BotInteraction.tenant_id == tenant_id,
            BotInteraction.sentiment.isnot(None)
        ).limit(1000).all()

        # Analyze sentiment shifts and triggers
        negative_keywords = []
        positive_responses = []
        escalation_patterns = defaultdict(int)

        for interaction in interactions:
            if interaction.sentiment == "negative":
                # Extract keywords that indicate frustration
                words = interaction.message_text.lower().split()
                negative_keywords.extend(words)

                # Check if conversation was escalated
                if interaction.intent in ["escalate", "human_help"]:
                    escalation_patterns["negative_to_escalation"] += 1

            elif interaction.sentiment == "positive":
                # Collect responses that led to positive sentiment
                if interaction.response_text:
                    positive_responses.append(interaction.response_text)

        # Generate recommendations
        top_negative_keywords = [word for word, count in Counter(negative_keywords).most_common(10)]

        return SentimentOptimization(
            de_escalation_triggers=top_negative_keywords,
            positive_reinforcement_responses=list(set(positive_responses[:5])),
            escalation_thresholds={"negative_interactions": 2}
        )

    def generate_personalization_rules(self, tenant_id: uuid.UUID) -> PersonalizationRules:
        """Generate personalization rules based on user data."""
        # Query group members and their interaction history
        members = self.db.query(GroupMember).filter(
            GroupMember.tenant_id == tenant_id
        ).all()

        user_preferences = defaultdict(list)
        segment_rules = {
            "paid_subscribers": {"upsell_priority": "high"},
            "free_users": {"feature_highlight": "premium_features"}
        }

        for member in members:
            if member.is_paid_subscriber:
                segment_rules["paid_subscribers"]["current_plan"] = "premium"
            else:
                segment_rules["free_users"]["upgrade_incentives"] = ["discount", "trial"]

        return PersonalizationRules(
            user_segment_rules=segment_rules,
            historical_preferences=user_preferences,
            upsell_opportunities={
                "paid_subscribers": ["plan_upgrade", "addon_features"],
                "free_users": ["basic_plan", "premium_trial"]
            }
        )

    def analyze_knowledge_gaps(self, tenant_id: uuid.UUID) -> KnowledgeGapAnalysis:
        """Identify knowledge gaps and efficiency issues."""
        # Query bot performance metrics
        metrics = self.db.query(BotPerformanceMetrics).filter(
            BotPerformanceMetrics.tenant_id == tenant_id,
            BotPerformanceMetrics.metric_type == "error_rate"
        ).all()

        # Query interactions that failed
        failed_interactions = self.db.query(BotInteraction).filter(
            BotInteraction.tenant_id == tenant_id,
            BotInteraction.intent == "fallback"  # Assuming fallback indicates failure
        ).all()

        # Analyze frequent failures
        failed_queries = [interaction.message_text for interaction in failed_interactions]
        frequent_failures = Counter(failed_queries).most_common(10)

        return KnowledgeGapAnalysis(
            frequent_failures=frequent_failures,
            long_conversation_paths=[],  # Would analyze conversation lengths
            slow_response_patterns=[]  # Would analyze latency by intent
        )

    def run_ab_test(self, tenant_id: uuid.UUID, test_config: Dict[str, Any]) -> str:
        """Set up and run an A/B test for monetization strategies."""
        # Create A/B test record
        test_id = str(uuid.uuid4())
        ab_test = ABTestResult(
            id=test_id,
            tenant_id=tenant_id,
            test_name=test_config["name"],
            test_type=test_config["type"],
            control_group=test_config["control"],
            variant_group=test_config["variant"]
        )

        self.db.add(ab_test)
        self.db.commit()

        return test_id

    def generate_optimization_recommendations(self, tenant_id: uuid.UUID) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []

        # Monetization optimization
        monetization_insights = self.analyze_monetization_triggers(tenant_id)
        if monetization_insights.profitable_intents:
            recommendations.append(OptimizationRecommendation(
                tenant_id=tenant_id,
                recommendation_type="monetization",
                target_metric="conversion_rate",
                current_value=0.05,  # Placeholder
                target_value=0.15,
                confidence_score=0.85,
                suggested_changes={
                    "focus_intents": [intent for intent, _ in monetization_insights.profitable_intents[:3]],
                    "response_templates": monetization_insights.top_performing_responses
                },
                implementation_priority="high",
                supporting_data={"profitable_intents": monetization_insights.profitable_intents},
                impact_estimate="Expected 200% increase in conversion rate for targeted intents"
            ))

        # Sentiment optimization
        sentiment_opt = self.optimize_sentiment_engagement(tenant_id)
        if sentiment_opt.de_escalation_triggers:
            recommendations.append(OptimizationRecommendation(
                tenant_id=tenant_id,
                recommendation_type="sentiment",
                target_metric="customer_satisfaction",
                current_value=0.75,  # Placeholder
                target_value=0.90,
                confidence_score=0.78,
                suggested_changes={
                    "de_escalation_keywords": sentiment_opt.de_escalation_triggers,
                    "positive_responses": sentiment_opt.positive_reinforcement_responses
                },
                implementation_priority="medium",
                supporting_data={"sentiment_patterns": len(sentiment_opt.de_escalation_triggers)},
                impact_estimate="Expected 20% improvement in user satisfaction scores"
            ))

        return recommendations
