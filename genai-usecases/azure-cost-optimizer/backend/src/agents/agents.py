"""
Azure Cost Optimization Multi-Agent System.

This module implements 5 specialized AI agents that work together to analyze
Azure cloud spending, detect anomalies, recommend optimizations, forecast costs,
and gamify the cost-saving experience:

1. Anomaly Detection Agent - Identifies cost spikes, underutilized resources
2. Optimization Recommendation Agent - Generates actionable cost-saving recommendations
3. Forecasting Agent - Projects future costs with and without optimizations
4. Gamification Agent - Awards points, badges, and health scores
5. HITL Checkpoint Agent - Pauses workflow for human review when needed

Each agent receives the shared CostState (TypedDict) and returns an updated CostState.
Agents use Google Gemini for LLM analysis with rule-based fallbacks for resilience.
"""

import os
import json
import uuid
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.models import (
    CostState, AgentDecision, Anomaly, Recommendation, Forecast,
    CONFIDENCE_THRESHOLDS, HEALTH_SCORE_WEIGHTS, POINTS_CONFIG,
    BADGE_DEFINITIONS, AnomalySeverity, RecommendationType, RiskLevel,
    HITLTriggerReason, HITLPriority
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class CostOptimizationAgents:
    """
    Container for all 5 cost optimization agents.

    Each agent is a method that takes the current CostState and returns
    an updated CostState. Agents are designed to be composed into a
    LangGraph workflow where state flows sequentially through them.
    """

    def __init__(self):
        """Initialize the agents with Gemini LLM."""
        logger.info("\nInitializing CostOptimizationAgents...")

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning("GOOGLE_API_KEY is not set. LLM calls will use rule-based fallbacks.")

        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1,
                google_api_key=google_api_key,
            )
            logger.info("Gemini LLM initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            self.llm = None

        logger.info("CostOptimizationAgents initialization complete.")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _call_gemini(self, prompt: str) -> str:
        """
        Invoke the Gemini LLM with error handling.

        Returns the text content of the response, or an empty string on failure.
        """
        if self.llm is None:
            logger.warning("LLM not available, returning empty response.")
            return ""

        try:
            response = self.llm.invoke(prompt)
            return response.content if response and response.content else ""
        except Exception as e:
            logger.error(f"Gemini LLM call failed: {e}")
            return ""

    def _parse_json_response(self, text: str) -> Dict:
        """
        Extract and parse JSON from an LLM response.

        Handles responses wrapped in markdown code blocks (```json ... ```)
        as well as raw JSON. Returns an empty dict on failure.
        """
        if not text:
            return {}

        try:
            # Strip markdown code block wrappers if present
            cleaned = text.strip()
            if cleaned.startswith("```"):
                # Remove opening ``` line (possibly ```json)
                first_newline = cleaned.index("\n")
                cleaned = cleaned[first_newline + 1:]
                # Remove closing ```
                if cleaned.rstrip().endswith("```"):
                    cleaned = cleaned.rstrip()[:-3].rstrip()

            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: find the first { ... } or [ ... ] block
        try:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(text[json_start:json_end])
        except json.JSONDecodeError:
            pass

        logger.warning("Failed to parse JSON from LLM response.")
        return {}

    # =========================================================================
    # Agent 1: Anomaly Detection Agent
    # =========================================================================

    def anomaly_detection_agent(self, state: CostState) -> CostState:
        """
        Agent 1: Anomaly Detection Agent

        Analyzes resource cost data and usage patterns to identify anomalies
        such as cost spikes, underutilized resources, and orphaned assets.

        Reads: resources, cost_history, current_monthly_spend
        Updates: anomalies, anomaly_count, anomaly_severity, agent_decisions
        """
        logger.info("\nAGENT 1: Anomaly Detection Agent")
        logger.info("=" * 80)

        start_time = time.time()
        anomalies: List[Dict[str, Any]] = []
        agent_decisions = state.get("agent_decisions", [])

        try:
            resources = state.get("resources", [])
            cost_history = state.get("cost_history", [])
            current_spend = state.get("current_monthly_spend", 0.0)

            # Prepare cost history summary (last 30 days)
            recent_history = cost_history[-30:] if len(cost_history) > 30 else cost_history

            # Build prompt for Gemini
            prompt = f"""You are an Azure cloud cost anomaly detector. Analyze the following data and identify cost anomalies.

CURRENT MONTHLY SPEND: ${current_spend:.2f}

RESOURCES ({len(resources)} total):
{json.dumps(resources[:20], indent=2, default=str)}

RECENT COST HISTORY (daily totals):
{json.dumps(recent_history[:30], indent=2, default=str)}

Identify anomalies. For each anomaly provide:
- resource_name: name of the affected resource
- resource_type: type of resource
- anomaly_type: one of "spike", "dip", "underutilized", "orphaned"
- severity: one of "low", "medium", "high", "critical"
- score: float 0-1 indicating confidence
- description: brief explanation
- affected_cost: the cost amount affected
- baseline_cost: what the expected/normal cost is

Return ONLY valid JSON in this format:
{{"anomalies": [{{...}}, ...]}}
"""

            response_text = self._call_gemini(prompt)
            parsed = self._parse_json_response(response_text)

            if parsed and "anomalies" in parsed:
                for a in parsed["anomalies"]:
                    anomaly = Anomaly(
                        resource_name=a.get("resource_name", "Unknown"),
                        resource_type=a.get("resource_type", "Unknown"),
                        anomaly_type=a.get("anomaly_type", "spike"),
                        severity=a.get("severity", "low"),
                        score=float(a.get("score", 0.5)),
                        description=a.get("description", ""),
                        affected_cost=float(a.get("affected_cost", 0.0)),
                        baseline_cost=float(a.get("baseline_cost", 0.0)),
                        detected_at=datetime.now().isoformat(),
                    )
                    anomalies.append(anomaly.to_dict())
                logger.info(f"LLM detected {len(anomalies)} anomalies.")
            else:
                # Rule-based fallback
                logger.info("Using rule-based fallback for anomaly detection.")
                anomalies = self._fallback_anomaly_detection(resources, cost_history)

        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            resources = state.get("resources", [])
            cost_history = state.get("cost_history", [])
            anomalies = self._fallback_anomaly_detection(resources, cost_history)

        # Determine overall anomaly severity from the highest-scored anomaly
        if anomalies:
            max_score = max(a.get("score", 0) for a in anomalies)
            if max_score >= 0.8:
                severity = AnomalySeverity.CRITICAL.value
            elif max_score >= 0.6:
                severity = AnomalySeverity.HIGH.value
            elif max_score >= 0.4:
                severity = AnomalySeverity.MEDIUM.value
            else:
                severity = AnomalySeverity.LOW.value
        else:
            severity = AnomalySeverity.NONE.value

        processing_time = time.time() - start_time

        decision = AgentDecision(
            agent_name="anomaly_detection_agent",
            decision=f"Detected {len(anomalies)} anomalies with severity: {severity}",
            confidence=max((a.get("score", 0) for a in anomalies), default=0.0),
            reasoning=f"Analyzed {len(state.get('resources', []))} resources and "
                      f"{len(state.get('cost_history', []))} days of cost history.",
            flags=[a.get("anomaly_type", "") for a in anomalies],
            recommendations=[],
            extracted_data={"anomaly_count": len(anomalies), "severity": severity},
            requires_human_review=(severity in [AnomalySeverity.HIGH.value, AnomalySeverity.CRITICAL.value]),
            processing_time=processing_time,
        )
        agent_decisions.append(decision.to_dict())

        state["anomalies"] = anomalies
        state["anomaly_count"] = len(anomalies)
        state["anomaly_severity"] = severity
        state["agent_decisions"] = agent_decisions

        logger.info(f"Anomaly detection complete: {len(anomalies)} anomalies, severity={severity}")
        return state

    def _fallback_anomaly_detection(
        self, resources: List[Dict], cost_history: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Rule-based fallback for anomaly detection when LLM is unavailable.

        - Flags resources with cpu_usage_pct < 15% as 'underutilized'
        - Flags daily costs > 1.3x the average as 'spike'
        """
        anomalies: List[Dict[str, Any]] = []

        # Underutilized resources
        for resource in resources:
            cpu = resource.get("cpu_usage_pct", resource.get("cpu_usage", None))
            if cpu is not None and float(cpu) < 15.0:
                anomaly = Anomaly(
                    resource_name=resource.get("name", resource.get("resource_name", "Unknown")),
                    resource_type=resource.get("type", resource.get("resource_type", "Unknown")),
                    anomaly_type="underutilized",
                    severity="medium",
                    score=0.6,
                    description=f"Resource CPU usage is very low at {cpu}%, indicating underutilization.",
                    affected_cost=float(resource.get("monthly_cost", resource.get("cost", 0))),
                    baseline_cost=float(resource.get("monthly_cost", resource.get("cost", 0))),
                    detected_at=datetime.now().isoformat(),
                )
                anomalies.append(anomaly.to_dict())

        # Cost spikes
        if cost_history:
            daily_costs = []
            for entry in cost_history:
                cost = entry.get("total_cost", entry.get("cost", entry.get("amount", 0)))
                if cost:
                    daily_costs.append(float(cost))

            if daily_costs:
                avg_cost = sum(daily_costs) / len(daily_costs)
                threshold = avg_cost * 1.3

                for i, entry in enumerate(cost_history):
                    cost = float(
                        entry.get("total_cost", entry.get("cost", entry.get("amount", 0)))
                    )
                    if cost > threshold:
                        anomaly = Anomaly(
                            resource_name=entry.get("date", f"Day {i}"),
                            resource_type="daily_aggregate",
                            anomaly_type="spike",
                            severity="high" if cost > avg_cost * 1.5 else "medium",
                            score=min(cost / avg_cost / 2.0, 1.0) if avg_cost > 0 else 0.5,
                            description=(
                                f"Daily cost ${cost:.2f} exceeds average ${avg_cost:.2f} "
                                f"by {((cost - avg_cost) / avg_cost * 100):.0f}%."
                            ),
                            affected_cost=cost,
                            baseline_cost=avg_cost,
                            detected_at=datetime.now().isoformat(),
                        )
                        anomalies.append(anomaly.to_dict())

        logger.info(f"Fallback anomaly detection found {len(anomalies)} anomalies.")
        return anomalies

    # =========================================================================
    # Agent 2: Optimization Recommendation Agent
    # =========================================================================

    def optimization_recommendation_agent(self, state: CostState) -> CostState:
        """
        Agent 2: Optimization Recommendation Agent

        Generates actionable cost-saving recommendations based on detected
        anomalies and resource configurations. Determines if human-in-the-loop
        review is required based on confidence, risk, and savings thresholds.

        Reads: anomalies, resources, cost_history, current_monthly_spend
        Updates: recommendations, total_potential_savings, optimization_confidence,
                 hitl_required, hitl_trigger_reasons, hitl_priority, agent_decisions
        """
        logger.info("\nAGENT 2: Optimization Recommendation Agent")
        logger.info("=" * 80)

        start_time = time.time()
        recommendations: List[Dict[str, Any]] = []
        agent_decisions = state.get("agent_decisions", [])

        try:
            anomalies = state.get("anomalies", [])
            resources = state.get("resources", [])
            cost_history = state.get("cost_history", [])
            current_spend = state.get("current_monthly_spend", 0.0)

            prompt = f"""You are an Azure cost optimization advisor. Based on the detected anomalies and resource data, generate specific optimization recommendations.

CURRENT MONTHLY SPEND: ${current_spend:.2f}

DETECTED ANOMALIES ({len(anomalies)}):
{json.dumps(anomalies[:15], indent=2, default=str)}

RESOURCES ({len(resources)} total):
{json.dumps(resources[:20], indent=2, default=str)}

For each recommendation provide:
- action: one of "right_size", "reserved_instance", "delete_unused", "tier_downgrade", "schedule_shutdown", "switch_region"
- resource_name: the target resource
- resource_type: type of the resource
- description: brief explanation of what to do and why
- estimated_savings: monthly dollar savings (float)
- confidence: float 0-1 indicating how confident you are
- risk_level: one of "low", "medium", "high"
- current_config: current configuration description
- recommended_config: recommended configuration description

Return ONLY valid JSON:
{{"recommendations": [{{...}}, ...]}}
"""

            response_text = self._call_gemini(prompt)
            parsed = self._parse_json_response(response_text)

            if parsed and "recommendations" in parsed:
                for r in parsed["recommendations"]:
                    rec = Recommendation(
                        id=str(uuid.uuid4()),
                        resource_name=r.get("resource_name", "Unknown"),
                        resource_type=r.get("resource_type", "Unknown"),
                        action=r.get("action", "right_size"),
                        description=r.get("description", ""),
                        estimated_savings=float(r.get("estimated_savings", 0.0)),
                        confidence=float(r.get("confidence", 0.5)),
                        risk_level=r.get("risk_level", "medium"),
                        current_config=r.get("current_config", ""),
                        recommended_config=r.get("recommended_config", ""),
                        status="pending",
                    )
                    recommendations.append(rec.to_dict())
                logger.info(f"LLM generated {len(recommendations)} recommendations.")
            else:
                logger.info("Using rule-based fallback for recommendations.")
                recommendations = self._fallback_recommendations(anomalies, resources)

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            anomalies = state.get("anomalies", [])
            resources = state.get("resources", [])
            recommendations = self._fallback_recommendations(anomalies, resources)

        # Calculate aggregate metrics
        total_potential_savings = sum(r.get("estimated_savings", 0) for r in recommendations)
        confidences = [r.get("confidence", 0) for r in recommendations]
        optimization_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )

        # Determine HITL requirements
        hitl_required = False
        hitl_trigger_reasons: List[str] = []
        hitl_priority = HITLPriority.LOW.value

        for rec in recommendations:
            conf = rec.get("confidence", 1.0)
            risk = rec.get("risk_level", "low")

            if conf < CONFIDENCE_THRESHOLDS["REQUIRES_REVIEW"]:
                hitl_required = True
                if HITLTriggerReason.LOW_CONFIDENCE.value not in hitl_trigger_reasons:
                    hitl_trigger_reasons.append(HITLTriggerReason.LOW_CONFIDENCE.value)

            if risk == RiskLevel.HIGH.value:
                hitl_required = True
                if HITLTriggerReason.HIGH_RISK_ACTION.value not in hitl_trigger_reasons:
                    hitl_trigger_reasons.append(HITLTriggerReason.HIGH_RISK_ACTION.value)

        if total_potential_savings > 2000:
            hitl_required = True
            if HITLTriggerReason.HIGH_SAVINGS.value not in hitl_trigger_reasons:
                hitl_trigger_reasons.append(HITLTriggerReason.HIGH_SAVINGS.value)

        # Set HITL priority based on trigger reasons
        if hitl_required:
            if HITLTriggerReason.HIGH_RISK_ACTION.value in hitl_trigger_reasons:
                hitl_priority = HITLPriority.HIGH.value
            elif HITLTriggerReason.HIGH_SAVINGS.value in hitl_trigger_reasons:
                hitl_priority = HITLPriority.MEDIUM.value
            elif HITLTriggerReason.LOW_CONFIDENCE.value in hitl_trigger_reasons:
                hitl_priority = HITLPriority.MEDIUM.value

        processing_time = time.time() - start_time

        decision = AgentDecision(
            agent_name="optimization_recommendation_agent",
            decision=f"Generated {len(recommendations)} recommendations, "
                     f"potential savings: ${total_potential_savings:.2f}",
            confidence=optimization_confidence,
            reasoning=f"Analyzed {len(state.get('anomalies', []))} anomalies across "
                      f"{len(state.get('resources', []))} resources.",
            flags=hitl_trigger_reasons,
            recommendations=[r.get("action", "") for r in recommendations],
            extracted_data={
                "total_potential_savings": total_potential_savings,
                "recommendation_count": len(recommendations),
                "hitl_required": hitl_required,
            },
            requires_human_review=hitl_required,
            processing_time=processing_time,
        )
        agent_decisions.append(decision.to_dict())

        state["recommendations"] = recommendations
        state["total_potential_savings"] = total_potential_savings
        state["optimization_confidence"] = optimization_confidence
        state["hitl_required"] = hitl_required
        state["hitl_trigger_reasons"] = hitl_trigger_reasons
        state["hitl_priority"] = hitl_priority
        state["agent_decisions"] = agent_decisions

        logger.info(
            f"Recommendations complete: {len(recommendations)} recs, "
            f"savings=${total_potential_savings:.2f}, HITL={hitl_required}"
        )
        return state

    def _fallback_recommendations(
        self, anomalies: List[Dict], resources: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Rule-based fallback for generating recommendations when LLM is unavailable.

        Generates basic recommendations from anomalies:
        - Underutilized resources -> right-size
        - Cost spikes -> schedule shutdown or investigate
        """
        recommendations: List[Dict[str, Any]] = []

        for anomaly in anomalies:
            anomaly_type = anomaly.get("anomaly_type", "")
            resource_name = anomaly.get("resource_name", "Unknown")
            resource_type = anomaly.get("resource_type", "Unknown")
            affected_cost = float(anomaly.get("affected_cost", 0))

            if anomaly_type == "underutilized":
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    resource_name=resource_name,
                    resource_type=resource_type,
                    action=RecommendationType.RIGHT_SIZE.value,
                    description=f"Right-size {resource_name} - currently underutilized. "
                                f"Consider downsizing to a smaller SKU to reduce costs.",
                    estimated_savings=round(affected_cost * 0.4, 2),
                    confidence=0.7,
                    risk_level=RiskLevel.LOW.value,
                    current_config="Current SKU (underutilized)",
                    recommended_config="Smaller SKU matching actual usage",
                    status="pending",
                )
                recommendations.append(rec.to_dict())

            elif anomaly_type == "spike":
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    resource_name=resource_name,
                    resource_type=resource_type,
                    action=RecommendationType.SCHEDULE_SHUTDOWN.value,
                    description=f"Investigate cost spike for {resource_name}. "
                                f"Consider scheduling non-production resources for shutdown.",
                    estimated_savings=round(affected_cost * 0.2, 2),
                    confidence=0.5,
                    risk_level=RiskLevel.MEDIUM.value,
                    current_config="Always running",
                    recommended_config="Scheduled shutdown during off-hours",
                    status="pending",
                )
                recommendations.append(rec.to_dict())

            elif anomaly_type == "orphaned":
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    resource_name=resource_name,
                    resource_type=resource_type,
                    action=RecommendationType.DELETE_UNUSED.value,
                    description=f"Delete orphaned resource {resource_name}. "
                                f"No active usage detected.",
                    estimated_savings=round(affected_cost, 2),
                    confidence=0.8,
                    risk_level=RiskLevel.LOW.value,
                    current_config="Orphaned / unused",
                    recommended_config="Delete resource",
                    status="pending",
                )
                recommendations.append(rec.to_dict())

        logger.info(f"Fallback generated {len(recommendations)} recommendations.")
        return recommendations

    # =========================================================================
    # Agent 3: Forecasting Agent
    # =========================================================================

    def forecasting_agent(self, state: CostState) -> CostState:
        """
        Agent 3: Forecasting Agent

        Projects future cloud costs for 30-day and 90-day windows, both with
        and without adoption of the recommended optimizations.

        Reads: cost_history, recommendations, current_monthly_spend
        Updates: forecast_30d, forecast_90d, forecast_with_optimization,
                 savings_if_adopted, forecast_trend, agent_decisions
        """
        logger.info("\nAGENT 3: Forecasting Agent")
        logger.info("=" * 80)

        start_time = time.time()
        agent_decisions = state.get("agent_decisions", [])

        forecast_30d = 0.0
        forecast_90d = 0.0
        forecast_with_optimization = 0.0
        savings_if_adopted = 0.0
        forecast_trend = "stable"

        try:
            cost_history = state.get("cost_history", [])
            recommendations = state.get("recommendations", [])
            current_spend = state.get("current_monthly_spend", 0.0)
            total_potential_savings = state.get("total_potential_savings", 0.0)

            prompt = f"""You are an Azure cloud cost forecaster. Based on the historical spending data and optimization recommendations, project future costs.

CURRENT MONTHLY SPEND: ${current_spend:.2f}
TOTAL POTENTIAL SAVINGS FROM RECOMMENDATIONS: ${total_potential_savings:.2f}

COST HISTORY (daily totals, most recent):
{json.dumps(cost_history[-30:], indent=2, default=str)}

ACTIVE RECOMMENDATIONS ({len(recommendations)}):
{json.dumps(recommendations[:10], indent=2, default=str)}

Provide:
- forecast_30d: projected total spend for next 30 days (float)
- forecast_90d: projected total spend for next 90 days (float)
- forecast_with_optimization: projected 30-day spend if all recommendations are adopted (float)
- savings_if_adopted: total dollar savings over 30 days if recommendations are adopted (float)
- trend: one of "increasing", "decreasing", "stable"

Return ONLY valid JSON:
{{"forecast_30d": 0.0, "forecast_90d": 0.0, "forecast_with_optimization": 0.0, "savings_if_adopted": 0.0, "trend": "stable"}}
"""

            response_text = self._call_gemini(prompt)
            parsed = self._parse_json_response(response_text)

            if parsed and "forecast_30d" in parsed:
                forecast_30d = float(parsed.get("forecast_30d", 0))
                forecast_90d = float(parsed.get("forecast_90d", 0))
                forecast_with_optimization = float(parsed.get("forecast_with_optimization", 0))
                savings_if_adopted = float(parsed.get("savings_if_adopted", 0))
                forecast_trend = parsed.get("trend", "stable")
                logger.info("LLM forecast generated successfully.")
            else:
                logger.info("Using rule-based fallback for forecasting.")
                result = self._fallback_forecast(cost_history, current_spend, total_potential_savings)
                forecast_30d = result["forecast_30d"]
                forecast_90d = result["forecast_90d"]
                forecast_with_optimization = result["forecast_with_optimization"]
                savings_if_adopted = result["savings_if_adopted"]
                forecast_trend = result["trend"]

        except Exception as e:
            logger.error(f"Forecasting error: {e}")
            cost_history = state.get("cost_history", [])
            current_spend = state.get("current_monthly_spend", 0.0)
            total_potential_savings = state.get("total_potential_savings", 0.0)
            result = self._fallback_forecast(cost_history, current_spend, total_potential_savings)
            forecast_30d = result["forecast_30d"]
            forecast_90d = result["forecast_90d"]
            forecast_with_optimization = result["forecast_with_optimization"]
            savings_if_adopted = result["savings_if_adopted"]
            forecast_trend = result["trend"]

        processing_time = time.time() - start_time

        decision = AgentDecision(
            agent_name="forecasting_agent",
            decision=f"30d forecast: ${forecast_30d:.2f}, trend: {forecast_trend}",
            confidence=0.7,
            reasoning=f"Projected costs using {len(state.get('cost_history', []))} days of history "
                      f"and {len(state.get('recommendations', []))} recommendations.",
            flags=[forecast_trend],
            recommendations=[],
            extracted_data={
                "forecast_30d": forecast_30d,
                "forecast_90d": forecast_90d,
                "forecast_with_optimization": forecast_with_optimization,
                "savings_if_adopted": savings_if_adopted,
            },
            requires_human_review=False,
            processing_time=processing_time,
        )
        agent_decisions.append(decision.to_dict())

        state["forecast_30d"] = forecast_30d
        state["forecast_90d"] = forecast_90d
        state["forecast_with_optimization"] = forecast_with_optimization
        state["savings_if_adopted"] = savings_if_adopted
        state["forecast_trend"] = forecast_trend
        state["agent_decisions"] = agent_decisions

        logger.info(
            f"Forecasting complete: 30d=${forecast_30d:.2f}, 90d=${forecast_90d:.2f}, "
            f"optimized=${forecast_with_optimization:.2f}, trend={forecast_trend}"
        )
        return state

    def _fallback_forecast(
        self,
        cost_history: List[Dict],
        current_spend: float,
        total_potential_savings: float,
    ) -> Dict[str, Any]:
        """
        Rule-based fallback for forecasting when LLM is unavailable.

        Uses simple linear projection from cost_history with 3% monthly growth.
        """
        daily_costs = []
        for entry in cost_history:
            cost = entry.get("total_cost", entry.get("cost", entry.get("amount", 0)))
            if cost:
                daily_costs.append(float(cost))

        if daily_costs:
            avg_daily = sum(daily_costs) / len(daily_costs)
        elif current_spend > 0:
            avg_daily = current_spend / 30.0
        else:
            avg_daily = 0.0

        monthly_growth_rate = 0.03  # 3% monthly growth assumption

        forecast_30d = round(avg_daily * 30 * (1 + monthly_growth_rate), 2)
        forecast_90d = round(
            avg_daily * 30 * (1 + monthly_growth_rate)
            + avg_daily * 30 * (1 + monthly_growth_rate) ** 2
            + avg_daily * 30 * (1 + monthly_growth_rate) ** 3,
            2,
        )
        forecast_with_optimization = round(forecast_30d - total_potential_savings, 2)
        savings_if_adopted = round(total_potential_savings, 2)

        # Determine trend
        if len(daily_costs) >= 14:
            first_half = sum(daily_costs[:len(daily_costs) // 2])
            second_half = sum(daily_costs[len(daily_costs) // 2:])
            if second_half > first_half * 1.05:
                trend = "increasing"
            elif second_half < first_half * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        logger.info(f"Fallback forecast: 30d=${forecast_30d}, trend={trend}")
        return {
            "forecast_30d": forecast_30d,
            "forecast_90d": forecast_90d,
            "forecast_with_optimization": max(forecast_with_optimization, 0),
            "savings_if_adopted": savings_if_adopted,
            "trend": trend,
        }

    # =========================================================================
    # Agent 4: Gamification Agent
    # =========================================================================

    def gamification_agent(self, state: CostState) -> CostState:
        """
        Agent 4: Gamification Agent (Rule-Based)

        Awards points, badges, and calculates a health score based on
        the current analysis results. No LLM call needed.

        Reads: recommendations, anomalies, resources, subscription_id
        Updates: points_earned, badges_unlocked, health_score, agent_decisions
        """
        logger.info("\nAGENT 4: Gamification Agent")
        logger.info("=" * 80)

        start_time = time.time()
        agent_decisions = state.get("agent_decisions", [])

        # ----- Points Calculation -----
        points = POINTS_CONFIG["analysis_triggered"]  # base points for running analysis

        anomalies = state.get("anomalies", [])
        recommendations = state.get("recommendations", [])
        resources = state.get("resources", [])
        anomaly_count = state.get("anomaly_count", len(anomalies))

        # Points for each anomaly detected (rewarding visibility)
        points += len(anomalies) * POINTS_CONFIG.get("anomaly_resolved", 75)

        # Points for recommendations reviewed (generated = available for review)
        points += len(recommendations) * POINTS_CONFIG.get("recommendation_reviewed", 25)

        # ----- Health Score Calculation (1-100) -----

        # Cost efficiency: fewer anomalies = better efficiency
        cost_efficiency = max(0, min(100, 100 - (anomaly_count * 10)))

        # Resource utilization: average CPU usage scaled to 0-100
        cpu_values = []
        for resource in resources:
            cpu = resource.get("cpu_usage_pct", resource.get("cpu_usage", None))
            if cpu is not None:
                cpu_values.append(float(cpu))
        resource_utilization = (
            min(100, (sum(cpu_values) / len(cpu_values))) if cpu_values else 50.0
        )

        # Optimization adoption: percentage of recommendations approved/implemented
        adopted_count = sum(
            1 for r in recommendations
            if r.get("status") in ("approved", "implemented")
        )
        optimization_adoption = (
            (adopted_count / len(recommendations) * 100) if recommendations else 0.0
        )

        # Anomaly frequency: fewer anomalies = better
        anomaly_frequency = max(0, min(100, 100 - (anomaly_count * 15)))

        # Weighted composite health score
        health_score = int(round(
            cost_efficiency * HEALTH_SCORE_WEIGHTS["cost_efficiency"]
            + resource_utilization * HEALTH_SCORE_WEIGHTS["resource_utilization"]
            + optimization_adoption * HEALTH_SCORE_WEIGHTS["optimization_adoption"]
            + anomaly_frequency * HEALTH_SCORE_WEIGHTS["anomaly_frequency"]
        ))
        health_score = max(1, min(100, health_score))

        # ----- Badge Evaluation -----
        badges_unlocked: List[str] = []
        total_savings = state.get("total_potential_savings", 0.0)

        for badge_name, badge_def in BADGE_DEFINITIONS.items():
            condition = badge_def.get("condition", "")

            if condition == "first_recommendation_adopted" and adopted_count >= 1:
                badges_unlocked.append(badge_name)
                points += badge_def.get("points", 0)

            elif condition == "total_savings_over_1000" and total_savings > 1000:
                badges_unlocked.append(badge_name)
                points += badge_def.get("points", 0)

            elif condition == "health_above_80_30days" and health_score >= 80:
                # In a POC, we award this if current health is above 80
                badges_unlocked.append(badge_name)
                points += badge_def.get("points", 0)

            elif condition == "adopted_10_recommendations" and adopted_count >= 10:
                badges_unlocked.append(badge_name)
                points += badge_def.get("points", 0)

            elif condition == "single_save_over_500":
                for r in recommendations:
                    if r.get("estimated_savings", 0) > 500:
                        badges_unlocked.append(badge_name)
                        points += badge_def.get("points", 0)
                        break

            # "7_day_streak" would require historical tracking; skip in POC

        processing_time = time.time() - start_time

        decision = AgentDecision(
            agent_name="gamification_agent",
            decision=f"Awarded {points} points, {len(badges_unlocked)} badges, health={health_score}",
            confidence=1.0,
            reasoning="Rule-based gamification scoring from analysis results.",
            flags=badges_unlocked,
            recommendations=[],
            extracted_data={
                "points_earned": points,
                "badges_unlocked": badges_unlocked,
                "health_score": health_score,
                "health_components": {
                    "cost_efficiency": round(cost_efficiency, 1),
                    "resource_utilization": round(resource_utilization, 1),
                    "optimization_adoption": round(optimization_adoption, 1),
                    "anomaly_frequency": round(anomaly_frequency, 1),
                },
            },
            requires_human_review=False,
            processing_time=processing_time,
        )
        agent_decisions.append(decision.to_dict())

        state["points_earned"] = points
        state["badges_unlocked"] = badges_unlocked
        state["health_score"] = health_score
        state["agent_decisions"] = agent_decisions

        logger.info(
            f"Gamification complete: points={points}, badges={badges_unlocked}, "
            f"health_score={health_score}"
        )
        return state

    # =========================================================================
    # Agent 5: HITL Checkpoint Agent
    # =========================================================================

    def hitl_checkpoint_agent(self, state: CostState) -> CostState:
        """
        Agent 5: Human-in-the-Loop Checkpoint Agent

        Controls workflow pausing and resumption based on HITL requirements.
        When hitl_required is True, sets status to 'pending_review' to pause
        the workflow. When a human decision is provided, processes it and
        resumes the workflow.

        Reads: hitl_required, hitl_human_decision, recommendations
        Updates: status, recommendations (statuses), agent_decisions
        """
        logger.info("\nAGENT 5: HITL Checkpoint Agent")
        logger.info("=" * 80)

        start_time = time.time()
        agent_decisions = state.get("agent_decisions", [])

        hitl_required = state.get("hitl_required", False)
        human_decision = state.get("hitl_human_decision", "")

        if human_decision:
            # Resuming after human review - process the decision
            logger.info(f"Processing human decision: {human_decision}")

            recommendations = state.get("recommendations", [])

            if human_decision == "approve_all":
                for rec in recommendations:
                    rec["status"] = "approved"
            elif human_decision == "reject_all":
                for rec in recommendations:
                    rec["status"] = "rejected"
            elif human_decision.startswith("approve:"):
                # Approve specific recommendation IDs (comma-separated)
                approved_ids = set(human_decision.replace("approve:", "").split(","))
                for rec in recommendations:
                    if rec.get("id") in approved_ids:
                        rec["status"] = "approved"
                    elif rec.get("status") == "pending":
                        rec["status"] = "rejected"
            elif human_decision == "request_reanalysis":
                state["status"] = "analyzing"
                logger.info("Human requested re-analysis.")
            else:
                # Default: treat as approve all
                for rec in recommendations:
                    rec["status"] = "approved"

            state["recommendations"] = recommendations
            state["status"] = "analyzing"

            processing_time = time.time() - start_time
            decision = AgentDecision(
                agent_name="hitl_checkpoint_agent",
                decision=f"Processed human decision: {human_decision}",
                confidence=1.0,
                reasoning="Human reviewer provided a decision on the recommendations.",
                flags=[],
                recommendations=[],
                extracted_data={
                    "human_decision": human_decision,
                    "reviewer": state.get("hitl_reviewer", ""),
                },
                requires_human_review=False,
                processing_time=processing_time,
            )
            agent_decisions.append(decision.to_dict())

        elif hitl_required:
            # Pause workflow for human review
            logger.info("HITL required - pausing workflow for human review.")
            state["status"] = "pending_review"

            processing_time = time.time() - start_time
            decision = AgentDecision(
                agent_name="hitl_checkpoint_agent",
                decision="Workflow paused for human review",
                confidence=1.0,
                reasoning=(
                    f"HITL triggered due to: {state.get('hitl_trigger_reasons', [])}. "
                    f"Priority: {state.get('hitl_priority', 'low')}."
                ),
                flags=state.get("hitl_trigger_reasons", []),
                recommendations=[],
                extracted_data={
                    "hitl_priority": state.get("hitl_priority", "low"),
                    "trigger_reasons": state.get("hitl_trigger_reasons", []),
                },
                requires_human_review=True,
                processing_time=processing_time,
            )
            agent_decisions.append(decision.to_dict())

        else:
            # No HITL needed, continue workflow
            logger.info("No HITL required - workflow continues.")

            processing_time = time.time() - start_time
            decision = AgentDecision(
                agent_name="hitl_checkpoint_agent",
                decision="No human review required, workflow continues",
                confidence=1.0,
                reasoning="All recommendations meet confidence and risk thresholds.",
                flags=[],
                recommendations=[],
                extracted_data={},
                requires_human_review=False,
                processing_time=processing_time,
            )
            agent_decisions.append(decision.to_dict())

        state["agent_decisions"] = agent_decisions

        logger.info(f"HITL checkpoint complete: status={state.get('status', 'unknown')}")
        return state


# =============================================================================
# Standalone Badge Checking Function
# =============================================================================

def check_and_unlock_badges(db, user_id: str, subscription_id: str = None) -> Dict[str, Any]:
    """
    Check badge conditions for a user and unlock any newly earned badges.

    This function queries the database for the user's current stats and checks
    all badge conditions. It returns newly unlocked badges and bonus points.

    Args:
        db: Database instance with gamification methods
        user_id: User ID to check badges for
        subscription_id: Optional subscription ID to get recommendations/savings data

    Returns:
        Dict with:
            - newly_unlocked: List of badge names that were just unlocked
            - bonus_points: Total points from newly unlocked badges
            - total_badges: List of all badges the user has
    """
    logger.info(f"Checking badges for user {user_id}")

    # Get current gamification stats
    user_stats = db.get_gamification(user_id)
    if not user_stats:
        logger.warning(f"No gamification stats found for user {user_id}")
        return {"newly_unlocked": [], "bonus_points": 0, "total_badges": []}

    current_badges = user_stats.get("badges", [])
    adopted_count = user_stats.get("recommendations_adopted", 0)

    # Get additional data for badge checks
    total_savings = 0.0
    max_single_savings = 0.0

    if subscription_id:
        # Get all recommendations for this subscription to calculate savings
        try:
            recommendations = db.get_recommendations(subscription_id)
            for rec in recommendations:
                savings = rec.get("estimated_savings", 0)
                if rec.get("status") in ("approved", "implemented"):
                    total_savings += savings
                max_single_savings = max(max_single_savings, savings)
        except Exception as e:
            logger.warning(f"Could not fetch recommendations: {e}")

    # Check each badge condition
    newly_unlocked = []
    bonus_points = 0

    for badge_name, badge_def in BADGE_DEFINITIONS.items():
        # Skip if already unlocked
        if badge_name in current_badges:
            continue

        condition = badge_def.get("condition", "")
        unlocked = False

        if condition == "first_recommendation_adopted" and adopted_count >= 1:
            unlocked = True
        elif condition == "total_savings_over_1000" and total_savings > 1000:
            unlocked = True
        elif condition == "adopted_10_recommendations" and adopted_count >= 10:
            unlocked = True
        elif condition == "single_save_over_500" and max_single_savings > 500:
            unlocked = True
        # Note: health_above_80_30days and 7_day_streak require historical tracking
        # These are only checked during full analysis in gamification_agent

        if unlocked:
            newly_unlocked.append(badge_name)
            bonus_points += badge_def.get("points", 0)
            logger.info(f"Badge unlocked: {badge_name} (+{badge_def.get('points', 0)} points)")

    # Update database with newly unlocked badges and bonus points
    if newly_unlocked:
        db.update_gamification(
            user_id=user_id,
            points=bonus_points,
            badges=newly_unlocked
        )
        all_badges = current_badges + newly_unlocked
        logger.info(f"Unlocked {len(newly_unlocked)} new badges for user {user_id}: {newly_unlocked}")
    else:
        all_badges = current_badges
        logger.info(f"No new badges unlocked for user {user_id}")

    return {
        "newly_unlocked": newly_unlocked,
        "bonus_points": bonus_points,
        "total_badges": all_badges
    }
