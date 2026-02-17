"""
Azure Cost Optimizer - FastAPI Backend
Single-file API with all endpoints for the POC.
"""

import os
import json
import uuid
import time
import asyncio
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

from src.database.cost_db import CostDatabase
from src.mock.data_generator import generate_all_mock_data
from src.agents.workflow import (
    create_cost_optimization_workflow,
    process_subscription_analysis,
    resume_from_hitl,
)
from src.agents.agents import check_and_unlock_badges

# =============================================================================
# Configuration
# =============================================================================
SECRET_KEY = "azure-cost-optimizer-poc-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# Global State
# =============================================================================
db: CostDatabase = None
workflow = None
hitl_queue: Dict[str, Dict] = {}

# =============================================================================
# Pydantic Models
# =============================================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class AnalyzeRequest(BaseModel):
    analysis_period: str = "30d"

class HITLDecisionRequest(BaseModel):
    decision: str  # approve, reject
    reviewer: str = ""
    notes: str = ""

class AwardSubmitRequest(BaseModel):
    nominated_user: str
    award_type: str
    reason: str
    points: int = 100

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

# =============================================================================
# Lifespan
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, workflow
    print("Starting Azure Cost Optimizer...")

    db = CostDatabase()
    db.init_database()

    # Seed mock data if empty
    subs = db.get_subscriptions()
    if not subs:
        print("Seeding mock data...")
        mock_data = generate_all_mock_data()
        db.seed_mock_data(mock_data)
        print("Mock data seeded.")

    # Create LangGraph workflow
    try:
        workflow = create_cost_optimization_workflow()
        print("LangGraph workflow created.")
    except Exception as e:
        print(f"Warning: Could not create workflow: {e}")
        workflow = None

    yield
    print("Shutting down...")

# =============================================================================
# App
# =============================================================================
app = FastAPI(
    title="Azure Cost Optimizer",
    description="Agentic AI system for Azure cost optimization with HITL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Auth Helpers
# =============================================================================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# =============================================================================
# Auth Endpoints
# =============================================================================
@app.post("/api/auth/login")
async def login(req: LoginRequest):
    import hashlib
    user = db.get_user(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Support both bcrypt and sha256 hashes (mock data uses sha256)
    stored_hash = user["password_hash"]
    sha256_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if stored_hash != sha256_hash:
        try:
            if not pwd_context.verify(req.password, stored_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
    }

# =============================================================================
# Hierarchy Endpoints
# =============================================================================
@app.get("/api/provisioning-entities")
async def list_provisioning_entities(user: dict = Depends(get_current_user)):
    from src.mock.data_generator import get_provisioning_entities
    return get_provisioning_entities()


@app.get("/api/organizations")
async def list_organizations(
    provisioning_entity_id: Optional[int] = Query(None),
    user: dict = Depends(get_current_user)
):
    from src.mock.data_generator import get_organizations
    return get_organizations(provisioning_entity_id)


# =============================================================================
# Subscription Endpoints
# =============================================================================
@app.get("/api/subscriptions")
async def list_subscriptions(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    subs = db.get_subscriptions()

    # Filter by provider if specified
    if provider:
        subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

    # Filter by provisioning entity if specified
    if provisioning_entity_id is not None:
        subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

    # Filter by organization if specified
    if organization_id is not None:
        subs = [s for s in subs if s.get("organization_id") == organization_id]

    return subs


@app.get("/api/subscriptions/{sub_id}")
async def get_subscription(sub_id: str, user: dict = Depends(get_current_user)):
    sub = db.get_subscription(sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    resources = db.get_resources(sub_id)
    cost_history = db.get_cost_history(sub_id, days=30)
    return {**sub, "resources": resources, "cost_history": cost_history}


@app.post("/api/subscriptions/{sub_id}/analyze")
async def analyze_subscription(
    sub_id: str,
    req: AnalyzeRequest,
    user: dict = Depends(get_current_user),
):
    sub = db.get_subscription(sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    resources = db.get_resources(sub_id)
    cost_history = db.get_cost_history(sub_id, days=90)

    subscription_data = {
        "subscription_id": sub_id,
        "subscription_name": sub["name"],
        "resources": resources,
        "cost_history": cost_history,
        "current_monthly_spend": sub["current_spend"],
        "analysis_period": req.analysis_period,
    }

    try:
        if workflow:
            final_state = await asyncio.to_thread(
                process_subscription_analysis,
                workflow,
                subscription_data,
                str(user["id"]),
            )
        else:
            # Fallback: run without workflow (mock analysis)
            final_state = _mock_analysis(subscription_data, str(user["id"]))

        analysis_id = final_state.get("analysis_id", str(uuid.uuid4()))

        # Save analysis
        db.save_analysis({
            "id": analysis_id,
            "subscription_id": sub_id,
            "user_id": str(user["id"]),
            "status": final_state.get("status", "completed"),
            "overall_confidence": final_state.get("overall_confidence", 0.75),
            "health_score": final_state.get("health_score", 65),
            "started_at": final_state.get("started_at", datetime.now().isoformat()),
            "completed_at": final_state.get("completed_at", datetime.now().isoformat()),
            "state_json": json.dumps(_sanitize_state(final_state)),
        })

        # Save anomalies
        anomalies = final_state.get("anomalies", [])
        for a in anomalies:
            a["analysis_id"] = analysis_id
            a["subscription_id"] = sub_id
        if anomalies:
            db.save_anomalies(anomalies)

        # Save recommendations
        recommendations = final_state.get("recommendations", [])
        for r in recommendations:
            r["analysis_id"] = analysis_id
            r["subscription_id"] = sub_id
        if recommendations:
            db.save_recommendations(recommendations)

        # Save forecast
        if final_state.get("forecast_30d"):
            db.save_forecast({
                "analysis_id": analysis_id,
                "subscription_id": sub_id,
                "forecast_30d": final_state.get("forecast_30d", 0),
                "forecast_90d": final_state.get("forecast_90d", 0),
                "forecast_with_optimization": final_state.get("forecast_with_optimization", 0),
                "savings_if_adopted": final_state.get("savings_if_adopted", 0),
                "trend": final_state.get("forecast_trend", "stable"),
                "confidence": final_state.get("overall_confidence", 0.75),
                "created_at": datetime.now().isoformat(),
            })

        # Update health score and last analyzed timestamp
        health = final_state.get("health_score", sub.get("health_score", 65))
        db.update_subscription_health(sub_id, health)
        db.update_subscription_last_analyzed(sub_id)

        # Update gamification
        points = final_state.get("points_earned", 10)
        badges = final_state.get("badges_unlocked", [])
        db.update_gamification(str(user["id"]), points=points, badges=badges, reviewed=0, adopted=0)

        # HITL queue
        if final_state.get("hitl_required"):
            hitl_entry = {
                "analysis_id": analysis_id,
                "subscription_id": sub_id,
                "subscription_name": sub["name"],
                "recommendations": [r for r in recommendations if r.get("status") == "pending"],
                "priority": final_state.get("hitl_priority", "medium"),
                "trigger_reasons": final_state.get("hitl_trigger_reasons", []),
                "overall_confidence": final_state.get("overall_confidence", 0.6),
                "total_potential_savings": final_state.get("total_potential_savings", 0),
                "agent_decisions": final_state.get("agent_decisions", []),
                "anomalies": anomalies,
                "health_score": health,
                "created_at": datetime.now().isoformat(),
            }
            hitl_queue[analysis_id] = hitl_entry

        return {
            "analysis_id": analysis_id,
            "status": final_state.get("status", "completed"),
            "hitl_required": final_state.get("hitl_required", False),
            "anomaly_count": len(anomalies),
            "recommendation_count": len(recommendations),
            "total_potential_savings": final_state.get("total_potential_savings", 0),
            "health_score": health,
            "overall_confidence": final_state.get("overall_confidence", 0.75),
        }

    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# =============================================================================
# Recommendations Endpoints
# =============================================================================
@app.get("/api/recommendations")
async def list_recommendations(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    subscription_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    recs = db.get_recommendations(sub_id=subscription_id, status=status)

    # Filter by hierarchy if specified
    if provider or provisioning_entity_id is not None or organization_id is not None:
        subs = db.get_subscriptions()

        # Filter subscriptions by provider
        if provider:
            subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

        # Filter by provisioning entity if specified
        if provisioning_entity_id is not None:
            subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

        # Filter by organization if specified
        if organization_id is not None:
            subs = [s for s in subs if s.get("organization_id") == organization_id]

        # Get list of subscription IDs that match the filters
        allowed_sub_ids = {s["id"] for s in subs}

        # Filter recommendations to only those from allowed subscriptions
        recs = [r for r in recs if r.get("subscription_id") in allowed_sub_ids]

    return recs


@app.get("/api/recommendations/pending")
async def pending_recommendations(user: dict = Depends(get_current_user)):
    recs = db.get_recommendations(status="pending")
    return recs


@app.post("/api/recommendations/{rec_id}/approve")
async def approve_recommendation(rec_id: str, user: dict = Depends(get_current_user)):
    try:
        # Get recommendation to extract subscription_id
        recommendation = db.get_recommendation(rec_id)
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        subscription_id = recommendation.get("subscription_id")

        # Update recommendation status and award points
        db.update_recommendation(rec_id, "approved", reviewed_by=user["username"])
        db.update_gamification(str(user["id"]), points=25, adopted=1)

        # Check and unlock badges
        badge_result = check_and_unlock_badges(db, str(user["id"]), subscription_id)

        return {
            "status": "approved",
            "recommendation_id": rec_id,
            "badges_unlocked": badge_result["newly_unlocked"],
            "bonus_points": badge_result["bonus_points"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommendations/{rec_id}/reject")
async def reject_recommendation(rec_id: str, user: dict = Depends(get_current_user)):
    try:
        # Get recommendation to extract subscription_id
        recommendation = db.get_recommendation(rec_id)
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        subscription_id = recommendation.get("subscription_id")

        # Update recommendation status and award points
        db.update_recommendation(rec_id, "rejected", reviewed_by=user["username"])
        db.update_gamification(str(user["id"]), points=10)

        # Check and unlock badges (in case user qualifies for other badges)
        badge_result = check_and_unlock_badges(db, str(user["id"]), subscription_id)

        return {
            "status": "rejected",
            "recommendation_id": rec_id,
            "badges_unlocked": badge_result["newly_unlocked"],
            "bonus_points": badge_result["bonus_points"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# HITL Queue Endpoints
# =============================================================================
@app.get("/api/hitl/queue")
async def get_hitl_queue(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    queue_list = sorted(
        hitl_queue.values(),
        key=lambda x: priority_order.get(x.get("priority", "low"), 3),
    )

    # Filter by hierarchy if specified
    if provider or provisioning_entity_id is not None or organization_id is not None:
        subs = db.get_subscriptions()

        # Filter subscriptions by provider
        if provider:
            subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

        # Filter by provisioning entity if specified
        if provisioning_entity_id is not None:
            subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

        # Filter by organization if specified
        if organization_id is not None:
            subs = [s for s in subs if s.get("organization_id") == organization_id]

        # Get list of subscription IDs that match the filters
        allowed_sub_ids = {s["id"] for s in subs}

        # Filter HITL queue to only those from allowed subscriptions
        queue_list = [item for item in queue_list if item.get("subscription_id") in allowed_sub_ids]

    return queue_list


@app.post("/api/hitl/review/{analysis_id}")
async def submit_hitl_review(
    analysis_id: str,
    req: HITLDecisionRequest,
    user: dict = Depends(get_current_user),
):
    if analysis_id not in hitl_queue:
        raise HTTPException(status_code=404, detail="Analysis not in HITL queue")

    entry = hitl_queue[analysis_id]

    # Update recommendation statuses
    for rec in entry.get("recommendations", []):
        rec_id = rec.get("id")
        if rec_id:
            new_status = "approved" if req.decision == "approve" else "rejected"
            db.update_recommendation(rec_id, new_status, reviewed_by=user["username"])

    # Try to resume workflow
    try:
        if workflow:
            await asyncio.to_thread(
                resume_from_hitl,
                workflow,
                analysis_id,
                req.decision,
                user["username"],
                req.notes,
            )
    except Exception as e:
        print(f"Workflow resume failed (non-critical): {e}")

    # Update analysis status
    db.update_analysis(analysis_id, {
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
    })

    # Add gamification points
    db.update_gamification(
        str(user["id"]),
        points=50,
        reviewed=len(entry.get("recommendations", [])),
        adopted=len(entry.get("recommendations", [])) if req.decision == "approve" else 0,
    )

    # Remove from queue
    del hitl_queue[analysis_id]

    return {
        "status": "reviewed",
        "analysis_id": analysis_id,
        "decision": req.decision,
    }

# =============================================================================
# Forecasting Endpoints
# =============================================================================
@app.get("/api/forecasts/{sub_id}")
async def get_subscription_forecasts(sub_id: str, user: dict = Depends(get_current_user)):
    forecasts = db.get_forecasts(sub_id)
    return forecasts


@app.get("/api/forecasts")
async def get_all_forecasts(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    subs = db.get_subscriptions()

    # Filter by provider if specified
    if provider:
        subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

    # Filter by provisioning entity if specified
    if provisioning_entity_id is not None:
        subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

    # Filter by organization if specified
    if organization_id is not None:
        subs = [s for s in subs if s.get("organization_id") == organization_id]

    all_forecasts = []
    for sub in subs:
        forecasts = db.get_forecasts(sub["id"])
        if forecasts:
            # Only use real forecasts from the database
            latest = forecasts[0]
            latest["subscription_name"] = sub["name"]
            latest["provider"] = sub.get("provider", "azure")
            all_forecasts.append(latest)

    return all_forecasts

# =============================================================================
# Gamification Endpoints
# =============================================================================
@app.get("/api/gamification/leaderboard")
async def get_leaderboard(user: dict = Depends(get_current_user)):
    return db.get_leaderboard()


@app.get("/api/gamification/my-stats")
async def get_my_stats(user: dict = Depends(get_current_user)):
    stats = db.get_gamification(str(user["id"]))
    if not stats:
        return {
            "user_id": str(user["id"]),
            "total_points": 0,
            "badges": [],
            "recommendations_adopted": 0,
            "recommendations_reviewed": 0,
            "current_streak": 0,
        }
    return stats


@app.get("/api/gamification/badges")
async def get_badges(user: dict = Depends(get_current_user)):
    from src.core.models import BADGE_DEFINITIONS
    return BADGE_DEFINITIONS


@app.post("/api/gamification/check-badges")
async def retroactive_badge_check(user: dict = Depends(get_current_user)):
    """
    Check and unlock badges for the current user based on their current stats.
    This endpoint is useful for retroactively unlocking badges for users who
    already have qualifying stats but badges weren't checked at the time.
    """
    try:
        # Get all subscriptions to check recommendations across all
        subscriptions = db.get_subscriptions()
        subscription_ids = [sub["id"] for sub in subscriptions]

        # Check badges for the user
        badge_result = check_and_unlock_badges(
            db,
            str(user["id"]),
            subscription_ids[0] if subscription_ids else None
        )

        return {
            "success": True,
            "newly_unlocked": badge_result["newly_unlocked"],
            "bonus_points": badge_result["bonus_points"],
            "total_badges": badge_result["total_badges"],
            "message": f"Badge check complete. Unlocked {len(badge_result['newly_unlocked'])} new badges."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gamification/awards")
async def submit_award(req: AwardSubmitRequest, user: dict = Depends(get_current_user)):
    award = {
        "nominated_by": user["username"],
        "nominated_user": req.nominated_user,
        "award_type": req.award_type,
        "reason": req.reason,
        "points": req.points,
        "created_at": datetime.now().isoformat(),
    }
    db.save_award(award)

    # Add points to nominated user
    nominated = db.get_user(req.nominated_user)
    if nominated:
        db.update_gamification(str(nominated["id"]), points=req.points)

    return {"status": "submitted", "award": award}


@app.get("/api/gamification/awards")
async def list_awards(user: dict = Depends(get_current_user)):
    return db.get_awards()

# =============================================================================
# Analytics Endpoints
# =============================================================================
@app.get("/api/analytics/cost-trends")
async def get_cost_trends(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    subs = db.get_subscriptions()

    # Filter by provider if specified
    if provider:
        subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

    # Filter by provisioning entity if specified
    if provisioning_entity_id is not None:
        subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

    # Filter by organization if specified
    if organization_id is not None:
        subs = [s for s in subs if s.get("organization_id") == organization_id]

    # Aggregate daily costs across filtered subscriptions for last 30 days
    daily_totals = {}
    for sub in subs:
        history = db.get_cost_history(sub["id"], days=30)
        for record in history:
            date = record["date"]
            if date not in daily_totals:
                daily_totals[date] = 0
            daily_totals[date] += record["daily_cost"]

    trends = [
        {"date": date, "cost": round(cost, 2)}
        for date, cost in sorted(daily_totals.items())
    ]
    return trends


@app.get("/api/analytics/health-scores")
async def get_health_scores(
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    subs = db.get_subscriptions()

    # Filter by provisioning entity if specified
    if provisioning_entity_id is not None:
        subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

    # Filter by organization if specified
    if organization_id is not None:
        subs = [s for s in subs if s.get("organization_id") == organization_id]

    return [
        {
            "id": s["id"],
            "name": s["name"],
            "health_score": s.get("health_score", 65),
            "environment": s.get("environment", ""),
        }
        for s in subs
    ]


@app.get("/api/analytics/summary")
async def get_summary(
    provider: str = Query(None, description="Filter by cloud provider (azure, aws)"),
    provisioning_entity_id: Optional[int] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    subs = db.get_subscriptions()

    # Filter by provider if specified
    if provider:
        subs = [s for s in subs if s.get("provider", "azure").lower() == provider.lower()]

    # Filter by provisioning entity if specified
    if provisioning_entity_id is not None:
        subs = [s for s in subs if s.get("provisioning_entity_id") == provisioning_entity_id]

    # Filter by organization if specified
    if organization_id is not None:
        subs = [s for s in subs if s.get("organization_id") == organization_id]

    total_spend = sum(s.get("current_spend", 0) for s in subs)
    avg_health = (
        sum(s.get("health_score", 0) for s in subs) / len(subs) if subs else 0
    )

    # Filter recommendations and anomalies by subscription provider
    sub_ids = [s["id"] for s in subs]
    all_recs = db.get_recommendations()
    filtered_recs = [r for r in all_recs if r.get("subscription_id") in sub_ids]
    total_savings = sum(r.get("estimated_savings", 0) for r in filtered_recs)

    all_anomalies = db.get_anomalies()
    filtered_anomalies = [a for a in all_anomalies if a.get("subscription_id") in sub_ids]
    total_anomalies = len(filtered_anomalies)

    return {
        "total_spend": round(total_spend, 2),
        "total_savings": round(total_savings, 2),
        "avg_health": round(avg_health, 1),
        "total_anomalies": total_anomalies,
        "total_recommendations": len(filtered_recs),
        "subscription_count": len(subs),
    }

# =============================================================================
# Mock Analysis Fallback (when workflow unavailable)
# =============================================================================
def _mock_analysis(subscription_data: dict, user_id: str) -> dict:
    """Generate a mock analysis result when LangGraph workflow is unavailable."""
    import random
    random.seed()

    resources = subscription_data.get("resources", [])
    current_spend = subscription_data.get("current_monthly_spend", 5000)
    sub_id = subscription_data.get("subscription_id", "")
    analysis_id = str(uuid.uuid4())

    # Mock anomalies
    anomalies = []
    for r in resources:
        cpu = r.get("cpu_usage_pct", 50)
        if cpu < 15:
            anomalies.append({
                "resource_name": r["name"],
                "resource_type": r["type"],
                "anomaly_type": "underutilized",
                "severity": "medium",
                "score": round(0.3 + random.random() * 0.4, 2),
                "description": f"{r['name']} has very low CPU usage ({cpu}%)",
                "affected_cost": r.get("monthly_cost", 100),
                "baseline_cost": r.get("monthly_cost", 100) * 0.5,
                "detected_at": datetime.now().isoformat(),
            })

    # Mock recommendations
    recommendations = []
    for a in anomalies:
        rec_id = str(uuid.uuid4())
        savings = round(a["affected_cost"] * 0.4, 2)
        recommendations.append({
            "id": rec_id,
            "resource_name": a["resource_name"],
            "resource_type": a["resource_type"],
            "action": "right_size",
            "description": f"Right-size {a['resource_name']} to reduce costs",
            "estimated_savings": savings,
            "confidence": round(0.65 + random.random() * 0.25, 2),
            "risk_level": "low",
            "current_config": "Current SKU",
            "recommended_config": "Smaller SKU",
            "status": "pending",
        })

    # Add a reserved instance recommendation
    if current_spend > 3000:
        rec_id = str(uuid.uuid4())
        ri_savings = round(current_spend * 0.15, 2)
        recommendations.append({
            "id": rec_id,
            "resource_name": "Subscription-wide",
            "resource_type": "Virtual Machine",
            "action": "reserved_instance",
            "description": "Switch eligible VMs to 1-year Reserved Instances",
            "estimated_savings": ri_savings,
            "confidence": round(0.70 + random.random() * 0.2, 2),
            "risk_level": "medium",
            "current_config": "Pay-As-You-Go",
            "recommended_config": "1-Year Reserved Instance",
            "status": "pending",
        })

    total_savings = sum(r["estimated_savings"] for r in recommendations)
    avg_confidence = (
        sum(r["confidence"] for r in recommendations) / len(recommendations)
        if recommendations
        else 0.75
    )

    # Determine HITL
    hitl_required = avg_confidence < 0.85 or any(
        r["risk_level"] == "high" for r in recommendations
    )
    hitl_reasons = []
    if avg_confidence < 0.85:
        hitl_reasons.append("low_confidence")
    if any(r["risk_level"] in ("medium", "high") for r in recommendations):
        hitl_reasons.append("high_risk_action")
    if total_savings > 2000:
        hitl_reasons.append("high_savings")

    # Health score
    anomaly_count = len(anomalies)
    avg_cpu = (
        sum(r.get("cpu_usage_pct", 50) for r in resources) / len(resources)
        if resources
        else 50
    )
    cost_eff = max(0, min(100, 100 - anomaly_count * 10))
    util_score = min(100, avg_cpu * 1.5)
    health = int(cost_eff * 0.3 + util_score * 0.25 + 50 * 0.25 + max(0, 100 - anomaly_count * 15) * 0.2)

    # Build realistic agent_decisions
    agent_decisions = [
        {
            "agent_name": "Anomaly Detection Agent",
            "decision": f"Detected {anomaly_count} anomalies across {len(resources)} resources",
            "confidence": round(0.75 + random.random() * 0.15, 2),
            "reasoning": f"Scanned {len(resources)} resources and {len(subscription_data.get('cost_history', []))} days of cost history. "
                         f"Identified {anomaly_count} underutilized resources with CPU usage below 15% threshold. "
                         + (f"Highest anomaly score: {max((a['score'] for a in anomalies), default=0):.2f}." if anomalies else "No significant anomalies found."),
            "flags": list(set(a.get("anomaly_type", "") for a in anomalies)),
            "recommendations": [],
            "extracted_data": {"anomaly_count": anomaly_count, "severity": "medium" if anomaly_count > 0 else "none", "resources_scanned": len(resources)},
            "requires_human_review": anomaly_count > 3,
            "processing_time": round(1.2 + random.random() * 1.5, 1),
        },
        {
            "agent_name": "Optimization Recommendation Agent",
            "decision": f"Generated {len(recommendations)} recommendations with ${total_savings:,.0f} potential savings",
            "confidence": round(avg_confidence, 2),
            "reasoning": f"Analyzed {anomaly_count} anomalies and generated {len(recommendations)} actionable recommendations. "
                         f"Total potential monthly savings: ${total_savings:,.2f}. "
                         f"Average confidence: {avg_confidence:.0%}. "
                         + (f"HITL triggered due to: {', '.join(hitl_reasons)}." if hitl_required else "All recommendations auto-approved (high confidence)."),
            "flags": hitl_reasons,
            "recommendations": [r["action"] for r in recommendations],
            "extracted_data": {"recommendation_count": len(recommendations), "total_savings": round(total_savings, 2), "actions": list(set(r["action"] for r in recommendations))},
            "requires_human_review": hitl_required,
            "processing_time": round(1.5 + random.random() * 2.0, 1),
        },
        {
            "agent_name": "HITL Checkpoint Agent",
            "decision": "Workflow paused for human review" if hitl_required else "Auto-approved - no human review needed",
            "confidence": round(avg_confidence, 2),
            "reasoning": (f"Human review required: {', '.join(hitl_reasons)}. Priority: {'high' if 'high_risk_action' in hitl_reasons else 'medium'}." if hitl_required
                          else "All recommendations meet confidence threshold (>85%). Proceeding automatically."),
            "flags": ["requires_review"] if hitl_required else ["auto_approved"],
            "recommendations": [],
            "extracted_data": {"hitl_required": hitl_required, "priority": "high" if "high_risk_action" in hitl_reasons else "medium"},
            "requires_human_review": hitl_required,
            "processing_time": round(0.3 + random.random() * 0.4, 1),
        },
        {
            "agent_name": "Forecasting Agent",
            "decision": f"Projected 30-day cost: ${current_spend * 1.03:,.0f} (3% growth trend)",
            "confidence": round(0.70 + random.random() * 0.15, 2),
            "reasoning": f"Analyzed cost trends over {len(subscription_data.get('cost_history', []))} days. "
                         f"Current monthly spend: ${current_spend:,.2f}. Projected 30-day: ${current_spend * 1.03:,.2f}. "
                         f"If all optimizations adopted, projected spend drops to ${current_spend * 0.85:,.2f} (saving ${total_savings:,.2f}/mo).",
            "flags": ["increasing_trend"],
            "recommendations": [],
            "extracted_data": {"forecast_30d": round(current_spend * 1.03, 2), "forecast_90d": round(current_spend * 3.1, 2), "trend": "increasing"},
            "requires_human_review": False,
            "processing_time": round(1.0 + random.random() * 1.0, 1),
        },
        {
            "agent_name": "Gamification Agent",
            "decision": f"Health score: {health}/100. Earned {10 + len(anomalies) * 5} points",
            "confidence": 0.95,
            "reasoning": f"Health score breakdown - Cost Efficiency: {cost_eff:.0f}/100 (weight: 30%), "
                         f"Resource Utilization: {util_score:.0f}/100 (weight: 25%), "
                         f"Optimization Adoption: 50/100 (weight: 25%), "
                         f"Anomaly Frequency: {max(0, 100 - anomaly_count * 15):.0f}/100 (weight: 20%). "
                         f"Final weighted score: {health}/100.",
            "flags": [],
            "recommendations": [],
            "extracted_data": {
                "health_score": health,
                "health_components": {
                    "cost_efficiency": round(cost_eff, 1),
                    "resource_utilization": round(util_score, 1),
                    "optimization_adoption": 50.0,
                    "anomaly_frequency": round(max(0, 100 - anomaly_count * 15), 1),
                },
                "points_earned": 10 + len(anomalies) * 5,
            },
            "requires_human_review": False,
            "processing_time": round(0.5 + random.random() * 0.5, 1),
        },
    ]

    return {
        "analysis_id": analysis_id,
        "subscription_id": sub_id,
        "status": "pending_review" if hitl_required else "completed",
        "anomalies": anomalies,
        "anomaly_count": anomaly_count,
        "anomaly_severity": "medium" if anomaly_count > 0 else "none",
        "recommendations": recommendations,
        "total_potential_savings": round(total_savings, 2),
        "optimization_confidence": round(avg_confidence, 2),
        "forecast_30d": round(current_spend * 1.03, 2),
        "forecast_90d": round(current_spend * 3.1, 2),
        "forecast_with_optimization": round(current_spend * 0.85, 2),
        "savings_if_adopted": round(total_savings, 2),
        "forecast_trend": "increasing",
        "health_score": health,
        "points_earned": 10 + len(anomalies) * 5,
        "badges_unlocked": [],
        "hitl_required": hitl_required,
        "hitl_trigger_reasons": hitl_reasons,
        "hitl_priority": "high" if "high_risk_action" in hitl_reasons else "medium",
        "overall_confidence": round(avg_confidence, 2),
        "agent_decisions": agent_decisions,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
    }


def _sanitize_state(state: dict) -> dict:
    """Make state JSON-serializable."""
    sanitized = {}
    for k, v in state.items():
        try:
            json.dumps(v)
            sanitized[k] = v
        except (TypeError, ValueError):
            sanitized[k] = str(v)
    return sanitized


def _save_analysis_results(final_state: dict, sub_id: str, sub: dict, user: dict):
    """Save analysis results to DB and HITL queue. Returns (analysis_id, health)."""
    analysis_id = final_state.get("analysis_id", str(uuid.uuid4()))

    db.save_analysis({
        "id": analysis_id,
        "subscription_id": sub_id,
        "user_id": str(user["id"]),
        "status": final_state.get("status", "completed"),
        "overall_confidence": final_state.get("overall_confidence", 0.75),
        "health_score": final_state.get("health_score", 65),
        "started_at": final_state.get("started_at", datetime.now().isoformat()),
        "completed_at": final_state.get("completed_at", datetime.now().isoformat()),
        "state_json": json.dumps(_sanitize_state(final_state)),
    })

    anomalies = final_state.get("anomalies", [])
    for a in anomalies:
        a["analysis_id"] = analysis_id
        a["subscription_id"] = sub_id
    if anomalies:
        db.save_anomalies(anomalies)

    recommendations = final_state.get("recommendations", [])
    for r in recommendations:
        r["analysis_id"] = analysis_id
        r["subscription_id"] = sub_id
    if recommendations:
        db.save_recommendations(recommendations)

    if final_state.get("forecast_30d"):
        db.save_forecast({
            "analysis_id": analysis_id,
            "subscription_id": sub_id,
            "forecast_30d": final_state.get("forecast_30d", 0),
            "forecast_90d": final_state.get("forecast_90d", 0),
            "forecast_with_optimization": final_state.get("forecast_with_optimization", 0),
            "savings_if_adopted": final_state.get("savings_if_adopted", 0),
            "trend": final_state.get("forecast_trend", "stable"),
            "confidence": final_state.get("overall_confidence", 0.75),
            "created_at": datetime.now().isoformat(),
        })

    health = final_state.get("health_score", sub.get("health_score", 65))
    db.update_subscription_health(sub_id, health)
    db.update_subscription_last_analyzed(sub_id)

    points = final_state.get("points_earned", 10)
    badges = final_state.get("badges_unlocked", [])
    db.update_gamification(str(user["id"]), points=points, badges=badges, reviewed=0, adopted=0)

    if final_state.get("hitl_required"):
        hitl_entry = {
            "analysis_id": analysis_id,
            "subscription_id": sub_id,
            "subscription_name": sub["name"],
            "recommendations": [r for r in recommendations if r.get("status") == "pending"],
            "priority": final_state.get("hitl_priority", "medium"),
            "trigger_reasons": final_state.get("hitl_trigger_reasons", []),
            "overall_confidence": final_state.get("overall_confidence", 0.6),
            "total_potential_savings": final_state.get("total_potential_savings", 0),
            "agent_decisions": final_state.get("agent_decisions", []),
            "anomalies": anomalies,
            "health_score": health,
            "created_at": datetime.now().isoformat(),
        }
        hitl_queue[analysis_id] = hitl_entry

    return analysis_id, health


# =============================================================================
# SSE Streaming Analysis Endpoint
# =============================================================================
@app.post("/api/subscriptions/{sub_id}/analyze-stream")
async def analyze_subscription_stream(
    sub_id: str,
    req: AnalyzeRequest,
    user: dict = Depends(get_current_user),
):
    """Stream analysis progress via Server-Sent Events."""
    sub = db.get_subscription(sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    resources = db.get_resources(sub_id)
    cost_history = db.get_cost_history(sub_id, days=90)

    subscription_data = {
        "subscription_id": sub_id,
        "subscription_name": sub["name"],
        "resources": resources,
        "cost_history": cost_history,
        "current_monthly_spend": sub["current_spend"],
        "analysis_period": req.analysis_period,
    }

    event_queue = queue.Queue()

    def run_streaming_analysis():
        try:
            final_state = _mock_analysis_with_callbacks(
                subscription_data, str(user["id"]), event_queue
            )
            # Save results
            analysis_id, health = _save_analysis_results(final_state, sub_id, sub, user)
            event_queue.put(("complete", {
                "analysis_id": analysis_id,
                "status": final_state.get("status", "completed"),
                "hitl_required": final_state.get("hitl_required", False),
                "anomaly_count": len(final_state.get("anomalies", [])),
                "recommendation_count": len(final_state.get("recommendations", [])),
                "total_potential_savings": final_state.get("total_potential_savings", 0),
                "health_score": health,
                "overall_confidence": final_state.get("overall_confidence", 0.75),
                "agent_decisions": final_state.get("agent_decisions", []),
            }))
        except Exception as e:
            event_queue.put(("error", {"message": str(e)}))

    async def event_generator():
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, run_streaming_analysis)

        while True:
            try:
                event_type, data = await asyncio.to_thread(event_queue.get, timeout=120)
                yield f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"
                if event_type in ("complete", "error"):
                    break
            except Exception:
                yield f"event: error\ndata: {json.dumps({'message': 'Timeout'})}\n\n"
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


def _mock_analysis_with_callbacks(subscription_data: dict, user_id: str, event_q: queue.Queue) -> dict:
    """Run mock analysis with streaming events for each agent step."""
    import random

    # First run the full mock analysis to get the final state
    final_state = _mock_analysis(subscription_data, user_id)
    agent_decisions = final_state.get("agent_decisions", [])

    # Agent steps with randomized processing times (base_time +/- 40%)
    agent_steps = [
        ("anomaly_detection", "Anomaly Detection Agent", round(1.8 + random.uniform(-0.7, 0.7), 1)),
        ("optimization_recommendation", "Optimization Recommendation Agent", round(2.5 + random.uniform(-1.0, 1.0), 1)),
        ("hitl_checkpoint", "HITL Checkpoint Agent", round(0.8 + random.uniform(-0.3, 0.3), 1)),
        ("forecasting", "Forecasting Agent", round(1.5 + random.uniform(-0.6, 0.6), 1)),
        ("gamification", "Gamification Agent", round(1.0 + random.uniform(-0.4, 0.4), 1)),
    ]

    # Send pipeline start
    event_q.put(("pipeline_start", {
        "analysis_id": final_state.get("analysis_id", ""),
        "subscription_name": subscription_data.get("subscription_name", ""),
        "agents": [name for _, name, _ in agent_steps],
    }))

    # Stream each agent step
    for i, (key, display_name, delay) in enumerate(agent_steps):
        # Agent starting
        event_q.put(("agent_start", {
            "agent_key": key,
            "agent_name": display_name,
            "step": i + 1,
            "total_steps": len(agent_steps),
        }))

        # Simulate processing time
        time.sleep(delay)

        # Agent completed - send its decision
        decision = agent_decisions[i] if i < len(agent_decisions) else {
            "agent_name": display_name,
            "decision": "Completed",
            "confidence": 0.8,
            "reasoning": "Processing complete.",
            "processing_time": delay,
        }

        event_q.put(("agent_complete", {
            "agent_key": key,
            "agent_name": display_name,
            "step": i + 1,
            "total_steps": len(agent_steps),
            "decision": decision,
        }))

    return final_state


# =============================================================================
# Analysis Detail Endpoint
# =============================================================================
@app.get("/api/analyses/{analysis_id}")
async def get_analysis_detail(analysis_id: str, user: dict = Depends(get_current_user)):
    """Get full analysis details including agent_decisions from state_json."""
    analysis = db.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# =============================================================================
# Chat Endpoint (Conversational AI)
# =============================================================================
@app.post("/api/chat")
async def chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    """Conversational AI endpoint for querying cost data."""
    subs = db.get_subscriptions()
    all_recs = db.get_recommendations()
    all_anomalies = db.get_anomalies()

    summary_data = {
        "subscriptions": [{"name": s["name"], "id": s["id"], "spend": s["current_spend"],
                           "health": s["health_score"], "environment": s["environment"]} for s in subs],
        "total_spend": sum(s["current_spend"] for s in subs),
        "total_recommendations": len(all_recs),
        "total_anomalies": len(all_anomalies),
        "pending_recommendations": len([r for r in all_recs if r["status"] == "pending"]),
        "recent_anomalies": all_anomalies[:5],
        "recent_recommendations": all_recs[:5],
    }

    # Try LLM-powered response
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No API key")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            google_api_key=api_key,
        )
        system_prompt = (
            "You are Nebula AI, an Azure Cost Optimization assistant. "
            "Answer questions about the user's Azure cloud spending, resources, anomalies, and recommendations. "
            "Be concise, helpful, and use dollar amounts where relevant. "
            "If asked about a specific resource, look for it in the data.\n\n"
            f"CURRENT DATA:\n{json.dumps(summary_data, indent=2, default=str)[:5000]}\n\n"
            f"USER: {req.message}\n\n"
            "Respond in 2-4 sentences."
        )
        response = await asyncio.to_thread(llm.invoke, system_prompt)
        answer = response.content
    except Exception:
        answer = _fallback_chat_response(req.message, summary_data)

    return {"response": answer}


def _fallback_chat_response(message: str, data: dict) -> str:
    """Rule-based chat fallback when LLM is unavailable."""
    msg = message.lower()

    if "highest spending" in msg or "most expensive" in msg or "top spend" in msg:
        subs = sorted(data["subscriptions"], key=lambda s: s["spend"], reverse=True)
        if subs:
            top = subs[0]
            return f"Your highest spending subscription is **{top['name']}** at **${top['spend']:,.2f}/month** ({top['environment']}). Its health score is {top['health']}/100."
        return "No subscriptions found."

    if "lowest" in msg and ("spend" in msg or "cost" in msg):
        subs = sorted(data["subscriptions"], key=lambda s: s["spend"])
        if subs:
            low = subs[0]
            return f"Your lowest spending subscription is **{low['name']}** at **${low['spend']:,.2f}/month**."
        return "No subscriptions found."

    if "anomal" in msg:
        count = data["total_anomalies"]
        recent = data.get("recent_anomalies", [])
        details = ""
        if recent:
            details = " Recent anomalies: " + ", ".join(f"{a.get('resource_name', 'Unknown')} ({a.get('anomaly_type', '')})" for a in recent[:3]) + "."
        return f"There are currently **{count} anomalies** detected across your subscriptions.{details} {data['pending_recommendations']} recommendations are pending review."

    if "recommend" in msg or "suggestion" in msg:
        total = data["total_recommendations"]
        pending = data["pending_recommendations"]
        return f"You have **{total} total recommendations**, of which **{pending} are pending** review. Visit the Recommendations page to approve or reject them."

    if "savings" in msg or "save" in msg or "optimi" in msg:
        recs = data.get("recent_recommendations", [])
        total_savings = sum(r.get("estimated_savings", 0) for r in recs)
        return f"Based on recent recommendations, you could save approximately **${total_savings:,.2f}/month**. Review and approve recommendations to realize these savings."

    if "health" in msg:
        subs = data["subscriptions"]
        if subs:
            avg = sum(s["health"] for s in subs) / len(subs)
            worst = min(subs, key=lambda s: s["health"])
            return f"Average health score across {len(subs)} subscriptions is **{avg:.0f}/100**. The lowest is **{worst['name']}** at **{worst['health']}/100**."
        return "No subscriptions found."

    if "how many" in msg and "subscription" in msg:
        count = len(data["subscriptions"])
        return f"You have **{count} subscriptions** being monitored. Total monthly spend is **${data['total_spend']:,.2f}**."

    if "hello" in msg or "hi" in msg or "hey" in msg:
        return f"Hello! I'm Nebula AI, your Azure cost optimization assistant. You have {len(data['subscriptions'])} subscriptions with **${data['total_spend']:,.2f}** total monthly spend. How can I help you today?"

    # Default
    return (
        f"I can help with questions about your Azure costs. You have **{len(data['subscriptions'])} subscriptions** "
        f"with **${data['total_spend']:,.2f}** total monthly spend, "
        f"**{data['total_anomalies']} anomalies**, and **{data['total_recommendations']} recommendations**. "
        f"Try asking about spending, anomalies, health scores, or savings opportunities."
    )


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["."], reload_excludes=[".venv", "databases", "__pycache__"])