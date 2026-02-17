"""
Core data models for Azure Cost Optimizer.
CostState (TypedDict), enums, dataclasses, and configuration constants.
"""

from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# =============================================================================
# Enums
# =============================================================================

class AnalysisStatus(Enum):
    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class AnomalySeverity(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(Enum):
    RIGHT_SIZE = "right_size"
    RESERVED_INSTANCE = "reserved_instance"
    DELETE_UNUSED = "delete_unused"
    TIER_DOWNGRADE = "tier_downgrade"
    SCHEDULE_SHUTDOWN = "schedule_shutdown"
    SWITCH_REGION = "switch_region"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HITLPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HITLTriggerReason(Enum):
    LOW_CONFIDENCE = "low_confidence"
    HIGH_RISK_ACTION = "high_risk_action"
    HIGH_SAVINGS = "high_savings"
    CONFLICTING_SIGNALS = "conflicting_signals"
    CRITICAL_RESOURCE = "critical_resource"


class ResourceType(Enum):
    VIRTUAL_MACHINE = "Virtual Machine"
    STORAGE_ACCOUNT = "Storage Account"
    SQL_DATABASE = "SQL Database"
    APP_SERVICE = "App Service"
    NETWORKING = "Networking"


class BadgeType(Enum):
    COST_CRUSHER = "Cost Crusher"
    CLOUD_GUARDIAN = "Cloud Guardian"
    OPTIMIZATION_HERO = "Optimization Hero"
    FIRST_SAVE = "First Save"
    STREAK_MASTER = "Streak Master"
    BIG_SAVER = "Big Saver"


# =============================================================================
# Configuration Constants
# =============================================================================

CONFIDENCE_THRESHOLDS = {
    "AUTO_APPROVE": 0.85,
    "REQUIRES_REVIEW": 0.60,
    "AUTO_FLAG": 0.40,
}

HEALTH_SCORE_WEIGHTS = {
    "cost_efficiency": 0.30,
    "resource_utilization": 0.25,
    "optimization_adoption": 0.25,
    "anomaly_frequency": 0.20,
}

BADGE_DEFINITIONS = {
    BadgeType.FIRST_SAVE.value: {
        "name": "First Save",
        "description": "Adopted your first optimization recommendation",
        "icon": "savings",
        "points": 50,
        "condition": "first_recommendation_adopted",
    },
    BadgeType.COST_CRUSHER.value: {
        "name": "Cost Crusher",
        "description": "Saved over $1,000 through optimizations",
        "icon": "trending_down",
        "points": 200,
        "condition": "total_savings_over_1000",
    },
    BadgeType.CLOUD_GUARDIAN.value: {
        "name": "Cloud Guardian",
        "description": "Maintained health score above 80 for 30 days",
        "icon": "shield",
        "points": 300,
        "condition": "health_above_80_30days",
    },
    BadgeType.OPTIMIZATION_HERO.value: {
        "name": "Optimization Hero",
        "description": "Adopted 10+ optimization recommendations",
        "icon": "star",
        "points": 500,
        "condition": "adopted_10_recommendations",
    },
    BadgeType.STREAK_MASTER.value: {
        "name": "Streak Master",
        "description": "Reviewed recommendations 7 days in a row",
        "icon": "local_fire_department",
        "points": 150,
        "condition": "7_day_streak",
    },
    BadgeType.BIG_SAVER.value: {
        "name": "Big Saver",
        "description": "Single optimization saved over $500",
        "icon": "rocket_launch",
        "points": 250,
        "condition": "single_save_over_500",
    },
}

POINTS_CONFIG = {
    "recommendation_adopted": 100,
    "recommendation_reviewed": 25,
    "anomaly_resolved": 75,
    "health_score_improved": 50,
    "analysis_triggered": 10,
}


# =============================================================================
# Dataclasses
# =============================================================================

@dataclass
class AgentDecision:
    agent_name: str
    decision: str
    confidence: float
    reasoning: str
    flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    requires_human_review: bool = False
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "decision": self.decision,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "flags": self.flags,
            "recommendations": self.recommendations,
            "extracted_data": self.extracted_data,
            "requires_human_review": self.requires_human_review,
            "processing_time": self.processing_time,
        }


@dataclass
class Anomaly:
    resource_name: str
    resource_type: str
    anomaly_type: str  # "spike", "dip", "underutilized", "orphaned"
    severity: str
    score: float  # 0-1
    description: str
    affected_cost: float
    baseline_cost: float
    detected_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "score": self.score,
            "description": self.description,
            "affected_cost": self.affected_cost,
            "baseline_cost": self.baseline_cost,
            "detected_at": self.detected_at or datetime.now().isoformat(),
        }


@dataclass
class Recommendation:
    id: str
    resource_name: str
    resource_type: str
    action: str
    description: str
    estimated_savings: float
    confidence: float
    risk_level: str
    current_config: str
    recommended_config: str
    status: str = "pending"  # pending, approved, rejected, implemented

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "action": self.action,
            "description": self.description,
            "estimated_savings": self.estimated_savings,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "current_config": self.current_config,
            "recommended_config": self.recommended_config,
            "status": self.status,
        }


@dataclass
class Forecast:
    subscription_id: str
    forecast_30d: float
    forecast_90d: float
    forecast_with_optimization: float
    savings_if_adopted: float
    trend: str  # "increasing", "decreasing", "stable"
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "forecast_30d": self.forecast_30d,
            "forecast_90d": self.forecast_90d,
            "forecast_with_optimization": self.forecast_with_optimization,
            "savings_if_adopted": self.savings_if_adopted,
            "trend": self.trend,
            "confidence": self.confidence,
        }


# =============================================================================
# CostState - Shared state between agents (LangGraph TypedDict)
# =============================================================================

class CostState(TypedDict, total=False):
    # Input identifiers
    subscription_id: str
    subscription_name: str
    analysis_id: str
    analysis_period: str  # "30d", "90d"
    user_id: str

    # Resource data (loaded from mock)
    resources: List[Dict[str, Any]]
    cost_history: List[Dict[str, Any]]
    current_monthly_spend: float

    # Anomaly Detection Agent outputs
    anomalies: List[Dict[str, Any]]
    anomaly_count: int
    anomaly_severity: str

    # Optimization Recommendation Agent outputs
    recommendations: List[Dict[str, Any]]
    total_potential_savings: float
    optimization_confidence: float

    # Forecasting Agent outputs
    forecast_30d: float
    forecast_90d: float
    forecast_with_optimization: float
    savings_if_adopted: float
    forecast_trend: str

    # Gamification Agent outputs
    points_earned: int
    badges_unlocked: List[str]
    health_score: int  # 1-100

    # Agent decisions (accumulated)
    agent_decisions: List[Dict[str, Any]]

    # HITL
    hitl_required: bool
    hitl_trigger_reasons: List[str]
    hitl_priority: str
    hitl_human_decision: str
    hitl_reviewer: str
    hitl_notes: str

    # Status
    status: str
    overall_confidence: float
    error: str
    started_at: str
    completed_at: str
