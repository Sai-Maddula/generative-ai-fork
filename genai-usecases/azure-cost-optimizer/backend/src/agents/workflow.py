"""
LangGraph workflow for Azure Cost Optimization multi-agent system.

This module constructs the StateGraph that orchestrates the agents with:
- Sequential analysis: Anomaly Detection -> Optimization Recommendation
- Human-in-the-Loop (HITL) checkpoint for low-confidence or high-risk decisions
- Cost Forecasting and Gamification agents post-review

Flow:
1. Anomaly Detection - Detects cost anomalies across Azure resources
2. Optimization Recommendation - Generates cost-saving recommendations
3. HITL Checkpoint (conditional) - Pauses for human review if triggered
4. Forecasting - Projects future costs with/without optimizations
5. Gamification - Awards points, badges, and health scores

Graph:
[START] -> [anomaly_detection] -> [optimization_recommendation] -> [hitl_check routing]
                                                                        |
                                                +-----------------------+
                                                |                       |
                                      [hitl_checkpoint]          [forecasting]
                                          (pauses)                      |
                                                |               [gamification]
                                      [resume with decision]            |
                                                |                    [END]
                                      [forecasting]
                                                |
                                      [gamification]
                                                |
                                              [END]
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.models import CostState, CONFIDENCE_THRESHOLDS, AnalysisStatus
from src.agents.agents import CostOptimizationAgents

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# Routing Functions
# =============================================================================


def route_after_optimization(state: CostState) -> Literal["hitl_checkpoint", "forecasting"]:
    """
    Routing function after Optimization Recommendation Agent.

    Determines whether human review is required before proceeding.

    Routes to:
    - hitl_checkpoint: if the optimization agent flagged HITL (low confidence,
      high-risk actions, large savings amounts, or conflicting signals)
    - forecasting: if recommendations are auto-approved (high confidence, low risk)

    Args:
        state: Current CostState with hitl_required flag set by the
               optimization recommendation agent.

    Returns:
        Next node name to route to.
    """
    hitl_required = state.get("hitl_required", False)

    if hitl_required:
        logger.info(
            "Routing to HITL checkpoint - human review required "
            f"(reasons: {state.get('hitl_trigger_reasons', [])})"
        )
        return "hitl_checkpoint"
    else:
        logger.info("Routing directly to forecasting - auto-approved")
        return "forecasting"


def route_after_hitl(state: CostState) -> Literal["forecasting", "__end__"]:
    """
    Routing function after HITL Checkpoint Agent.

    Determines whether to continue the workflow or pause for human input.

    Routes to:
    - forecasting: if a human decision has been recorded (workflow resumed),
      allowing the pipeline to continue with forecasting and gamification.
    - __end__: if the status is pending_review and no human decision exists,
      effectively pausing the workflow until a human resumes it.
    - forecasting (default): fallback to continue the pipeline.

    Args:
        state: Current CostState, potentially updated with hitl_human_decision
               after a human reviewer resumes the workflow.

    Returns:
        Next node name to route to, or END to pause.
    """
    human_decision = state.get("hitl_human_decision", "")
    status = state.get("status", "")

    # Human has already made a decision - continue the workflow
    if human_decision:
        logger.info(
            f"HITL resolved - human decision: '{human_decision}'. "
            "Continuing to forecasting."
        )
        return "forecasting"

    # Workflow is paused, waiting for human input
    if status == AnalysisStatus.PENDING_REVIEW.value:
        logger.info(
            "HITL pending - workflow paused. Waiting for human review."
        )
        return "__end__"

    # Default: continue
    logger.info("HITL routing fallback - continuing to forecasting.")
    return "forecasting"


# =============================================================================
# Workflow Factory
# =============================================================================


def create_cost_optimization_workflow() -> StateGraph:
    """
    Create and compile the LangGraph StateGraph for Azure cost optimization.

    The graph connects five specialized agents with conditional routing
    and HITL interrupt capability:

    1. Anomaly Detection Agent      - Scans resources for cost anomalies
    2. Optimization Recommendation  - Generates actionable savings recommendations
    3. HITL Checkpoint (conditional) - Pauses for human approval when needed
    4. Forecasting Agent            - Projects 30d/90d cost forecasts
    5. Gamification Agent           - Calculates points, badges, health score

    The workflow uses MemorySaver checkpointing to persist state across
    HITL pauses, allowing the workflow to be resumed after human review.

    Returns:
        Compiled LangGraph StateGraph with MemorySaver checkpointer.
    """
    logger.info("\nBuilding Azure Cost Optimization Workflow...")
    logger.info("=" * 50)

    # Initialize agents
    logger.info("Initializing CostOptimizationAgents...")
    agents = CostOptimizationAgents()

    # Create the state graph
    logger.info("Creating StateGraph...")
    workflow = StateGraph(CostState)

    # -------------------------------------------------------------------------
    # Add nodes
    # -------------------------------------------------------------------------
    logger.info("Adding agent nodes...")

    workflow.add_node("anomaly_detection", agents.anomaly_detection_agent)
    workflow.add_node("optimization_recommendation", agents.optimization_recommendation_agent)
    workflow.add_node("hitl_checkpoint", agents.hitl_checkpoint_agent)
    workflow.add_node("forecasting", agents.forecasting_agent)
    workflow.add_node("gamification", agents.gamification_agent)

    logger.info("  - anomaly_detection")
    logger.info("  - optimization_recommendation")
    logger.info("  - hitl_checkpoint")
    logger.info("  - forecasting")
    logger.info("  - gamification")

    # -------------------------------------------------------------------------
    # Set entry point
    # -------------------------------------------------------------------------
    workflow.set_entry_point("anomaly_detection")

    # -------------------------------------------------------------------------
    # Add edges
    # -------------------------------------------------------------------------
    logger.info("Adding edges...")

    # Anomaly Detection -> Optimization Recommendation (always)
    workflow.add_edge("anomaly_detection", "optimization_recommendation")

    # Optimization Recommendation -> HITL Checkpoint or Forecasting (conditional)
    workflow.add_conditional_edges(
        "optimization_recommendation",
        route_after_optimization,
        {
            "hitl_checkpoint": "hitl_checkpoint",
            "forecasting": "forecasting",
        },
    )

    # HITL Checkpoint -> Forecasting or END (conditional)
    workflow.add_conditional_edges(
        "hitl_checkpoint",
        route_after_hitl,
        {
            "forecasting": "forecasting",
            "__end__": END,
        },
    )

    # Forecasting -> Gamification (always)
    workflow.add_edge("forecasting", "gamification")

    # Gamification -> END (always)
    workflow.add_edge("gamification", END)

    # -------------------------------------------------------------------------
    # Compile with checkpointer
    # -------------------------------------------------------------------------
    logger.info("Compiling workflow with MemorySaver checkpointer...")
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)

    logger.info("Azure Cost Optimization Workflow compiled successfully.")
    logger.info("=" * 50)

    return compiled_graph


# =============================================================================
# Workflow Execution Helpers
# =============================================================================


def process_subscription_analysis(
    workflow,
    subscription_data: Dict[str, Any],
    user_id: str,
) -> CostState:
    """
    Process a subscription through the cost optimization workflow.

    Creates the initial CostState from subscription data and invokes the
    full multi-agent pipeline. The workflow may pause at the HITL checkpoint
    if human review is required, in which case the returned state will have
    status = "pending_review".

    Args:
        workflow: Compiled LangGraph (from create_cost_optimization_workflow).
        subscription_data: Dict containing at minimum:
            - subscription_id (str): Azure subscription ID
            - subscription_name (str): Human-readable subscription name
            - resources (list): List of resource dicts
            - cost_history (list): List of historical cost data dicts
            - current_monthly_spend (float): Current month's total spend
            - analysis_period (str, optional): "30d" or "90d" (default "30d")
        user_id: ID of the user triggering the analysis.

    Returns:
        Final CostState after workflow completes (or pauses at HITL).
    """
    logger.info("\n" + "=" * 50)
    logger.info("STARTING SUBSCRIPTION COST ANALYSIS")
    logger.info("=" * 50)

    # Generate a unique analysis ID for this run
    analysis_id = str(uuid.uuid4())

    # Build initial state
    initial_state: CostState = {
        # Identifiers
        "subscription_id": subscription_data.get("subscription_id", ""),
        "subscription_name": subscription_data.get("subscription_name", ""),
        "analysis_id": analysis_id,
        "analysis_period": subscription_data.get("analysis_period", "30d"),
        "user_id": user_id,
        # Resource data
        "resources": subscription_data.get("resources", []),
        "cost_history": subscription_data.get("cost_history", []),
        "current_monthly_spend": subscription_data.get("current_monthly_spend", 0.0),
        # Initialize outputs as empty / defaults
        "anomalies": [],
        "anomaly_count": 0,
        "anomaly_severity": "none",
        "recommendations": [],
        "total_potential_savings": 0.0,
        "optimization_confidence": 0.0,
        "forecast_30d": 0.0,
        "forecast_90d": 0.0,
        "forecast_with_optimization": 0.0,
        "savings_if_adopted": 0.0,
        "forecast_trend": "",
        "points_earned": 0,
        "badges_unlocked": [],
        "health_score": 0,
        "agent_decisions": [],
        # HITL
        "hitl_required": False,
        "hitl_trigger_reasons": [],
        "hitl_priority": "",
        "hitl_human_decision": "",
        "hitl_reviewer": "",
        "hitl_notes": "",
        # Status
        "status": AnalysisStatus.ANALYZING.value,
        "overall_confidence": 0.0,
        "error": "",
        "started_at": datetime.now().isoformat(),
        "completed_at": "",
    }

    logger.info(f"Analysis ID: {analysis_id}")
    logger.info(f"Subscription: {initial_state['subscription_name']} ({initial_state['subscription_id']})")
    logger.info(f"Resources: {len(initial_state['resources'])}")
    logger.info(f"User: {user_id}")

    # Configure with thread_id for checkpointing (enables HITL resume)
    config = {"configurable": {"thread_id": analysis_id}}

    # Invoke the workflow
    try:
        final_state = workflow.invoke(initial_state, config=config)
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise

    # Log result summary
    status = final_state.get("status", "unknown")
    logger.info("\n" + "=" * 50)

    if status == AnalysisStatus.PENDING_REVIEW.value:
        logger.info("ANALYSIS PAUSED - Awaiting human review")
        logger.info(f"  HITL Reasons: {final_state.get('hitl_trigger_reasons', [])}")
        logger.info(f"  Priority: {final_state.get('hitl_priority', 'N/A')}")
    elif status == AnalysisStatus.COMPLETED.value:
        logger.info("ANALYSIS COMPLETED")
        logger.info(f"  Anomalies found: {final_state.get('anomaly_count', 0)}")
        logger.info(f"  Recommendations: {len(final_state.get('recommendations', []))}")
        logger.info(f"  Potential savings: ${final_state.get('total_potential_savings', 0):.2f}")
        logger.info(f"  Health score: {final_state.get('health_score', 0)}/100")
    else:
        logger.info(f"ANALYSIS ENDED with status: {status}")

    logger.info("=" * 50)

    return final_state


def resume_from_hitl(
    workflow,
    analysis_id: str,
    human_decision: str,
    reviewer: str,
    notes: str = "",
) -> CostState:
    """
    Resume a paused workflow after human review at the HITL checkpoint.

    Retrieves the persisted state from the MemorySaver checkpoint using the
    analysis_id as the thread_id, updates it with the human decision, and
    re-invokes the workflow. The workflow continues from the hitl_checkpoint
    node through forecasting and gamification to completion.

    Args:
        workflow: Compiled LangGraph (same instance used for initial run).
        analysis_id: The analysis_id that was generated during
                     process_subscription_analysis (used as thread_id).
        human_decision: The reviewer's decision, e.g. "approved", "rejected",
                        or "modified".
        reviewer: Name or ID of the human reviewer.
        notes: Optional reviewer notes explaining the decision.

    Returns:
        Final CostState after the workflow completes the remaining stages
        (forecasting and gamification).

    Raises:
        ValueError: If no checkpoint state is found for the given analysis_id.
    """
    logger.info("\n" + "=" * 50)
    logger.info("RESUMING WORKFLOW WITH HUMAN DECISION")
    logger.info("=" * 50)
    logger.info(f"Analysis ID: {analysis_id}")
    logger.info(f"Decision: {human_decision}")
    logger.info(f"Reviewer: {reviewer}")

    # Build config matching the original thread
    config = {"configurable": {"thread_id": analysis_id}}

    # Retrieve existing checkpoint state
    existing_state = workflow.get_state(config)
    if existing_state is None or existing_state.values is None:
        raise ValueError(
            f"No checkpoint state found for analysis_id: {analysis_id}. "
            "The workflow may not have been paused at an HITL checkpoint."
        )

    logger.info(f"Retrieved checkpoint state (status: {existing_state.values.get('status', 'unknown')})")

    # Update the checkpoint state with human decision data
    workflow.update_state(
        config,
        {
            "hitl_human_decision": human_decision,
            "hitl_reviewer": reviewer,
            "hitl_notes": notes,
            "status": AnalysisStatus.APPROVED.value
            if human_decision == "approved"
            else AnalysisStatus.REJECTED.value
            if human_decision == "rejected"
            else AnalysisStatus.ANALYZING.value,
        },
    )

    # Resume the workflow from the checkpoint (pass None to continue)
    try:
        final_state = workflow.invoke(None, config=config)
    except Exception as e:
        logger.error(f"Workflow resume failed: {e}")
        raise

    # Log result
    logger.info("\n" + "=" * 50)
    logger.info("RESUMED ANALYSIS COMPLETED")
    logger.info(f"  Final status: {final_state.get('status', 'unknown')}")
    logger.info(f"  Anomalies: {final_state.get('anomaly_count', 0)}")
    logger.info(f"  Recommendations: {len(final_state.get('recommendations', []))}")
    logger.info(f"  Potential savings: ${final_state.get('total_potential_savings', 0):.2f}")
    logger.info(f"  30d forecast: ${final_state.get('forecast_30d', 0):.2f}")
    logger.info(f"  Health score: {final_state.get('health_score', 0)}/100")
    logger.info(f"  Points earned: {final_state.get('points_earned', 0)}")
    logger.info("=" * 50)

    return final_state
