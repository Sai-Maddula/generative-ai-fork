# Azure Cost Optimizer - Implementation Context

> This file preserves all context gathered during planning for the award panel demo enhancements.
> Reference this file if session context is lost.

---

## GOAL

Make the multi-agent AI system and Human-In-The-Loop workflow **visible and impressive** for an award panel demo, while keeping everything practical and functional. The user said: "They should be awestruck by seeing this. This should be practical to implement so that it doesn't become like shiny tool without use."

---

## 4 FEATURES TO IMPLEMENT

### Feature 1: Agent Workflow Tracker (Live Pipeline Visualization)
- Right-side Drawer opens when "Run Analysis" is clicked
- Vertical MUI Stepper showing 5 agents: Anomaly Detection -> Optimization -> HITL Check -> Forecasting -> Gamification
- Each step animates: pending -> running (spinner) -> completed (checkmark)
- Shows agent findings summary, reasoning, confidence after completion
- Backend SSE endpoint streams per-agent progress events

### Feature 2: Dedicated HITL Agent Review Page
- New route `/agent-review` with sidebar nav item + pending count badge
- Rich cards showing WHY human review is needed (trigger reasons as chips)
- Agent Decision Timeline showing chain of decisions
- Per-recommendation approve/reject checkboxes
- Notes field for reviewer reasoning

### Feature 3: Conversational AI Chat (Nebula AI)
- Floating FAB button (bottom-right) with gradient styling
- Opens 400x500 chat panel with message bubbles
- Backend `/api/chat` endpoint using Gemini + DB context
- Rule-based fallback for common questions

### Feature 4: Agent Explainability Panels
- "Why?" buttons on recommendation rows -> expandable reasoning sections
- Health Score Breakdown showing 4 weighted components
- Reusable `AgentReasoningPanel` component

---

## CURRENT PROJECT STRUCTURE

```
azure-cost-optimizer/
├── backend/
│   ├── main.py                          # FastAPI app (715 lines) - ALL endpoints
│   ├── src/
│   │   ├── agents/
│   │   │   ├── agents.py                # 5 agent methods in CostOptimizationAgents class
│   │   │   └── workflow.py              # LangGraph StateGraph + routing + helpers
│   │   ├── core/
│   │   │   └── models.py               # CostState TypedDict, AgentDecision dataclass, enums
│   │   ├── database/
│   │   │   └── cost_db.py              # SQLite database layer
│   │   └── mock/
│   │       └── data_generator.py        # Mock Azure data (5 subs, 3 users, 180 days)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx                      # Routes + Theme + LoginPage
│   │   ├── services/
│   │   │   └── api.js                   # Axios client + all API functions
│   │   ├── store/
│   │   │   └── store.js                 # Zustand: useAuthStore + useAppStore
│   │   └── components/
│   │       ├── Layout/Layout.jsx        # Sidebar (240px) + TopBar + content area
│   │       ├── Dashboard/Dashboard.jsx  # Stats cards + cost chart + sub cards
│   │       ├── Recommendations/Recommendations.jsx  # HITL alert + recs table
│   │       ├── Forecasting/Forecasting.jsx
│   │       ├── Gamification/Gamification.jsx
│   │       └── SubscriptionDetail/SubscriptionDetail.jsx
│   ├── package.json
│   └── vite.config.js                   # Proxy /api -> localhost:8000
```

---

## THEME & STYLING

```js
palette: {
  primary: '#0078d4',      // Azure Blue
  secondary: '#50e6ff',    // Cyan
  success: '#2e7d32',      // Green
  warning: '#ed6c02',      // Orange
  error: '#d32f2f',        // Red
  background: '#f5f5f5',   // Light gray
}
// Sidebar: linear-gradient(180deg, #0a1929 0%, #0d2744 100%)
// Card borderRadius: 12, Button borderRadius: 8
// Font: Inter, Segoe UI, Roboto
```

---

## KEY BACKEND DETAILS

### CostState (TypedDict) - All Fields
```python
# Identifiers
subscription_id, subscription_name, analysis_id, analysis_period, user_id

# Input data
resources: List[Dict], cost_history: List[Dict], current_monthly_spend: float

# Anomaly Detection outputs
anomalies: List[Dict], anomaly_count: int, anomaly_severity: str

# Optimization outputs
recommendations: List[Dict], total_potential_savings: float, optimization_confidence: float

# Forecasting outputs
forecast_30d, forecast_90d, forecast_with_optimization, savings_if_adopted: float
forecast_trend: str  # increasing/decreasing/stable

# Gamification outputs
points_earned: int, badges_unlocked: List[str], health_score: int (1-100)

# Agent decisions (accumulated by all agents)
agent_decisions: List[Dict]  # Each has: agent_name, decision, confidence, reasoning, flags, processing_time, extracted_data, requires_human_review

# HITL
hitl_required: bool, hitl_trigger_reasons: List[str], hitl_priority: str
hitl_human_decision: str, hitl_reviewer: str, hitl_notes: str

# Status
status: str, overall_confidence: float, error: str, started_at: str, completed_at: str
```

### AgentDecision dataclass fields
```python
agent_name: str, decision: str, confidence: float, reasoning: str
flags: List[str], recommendations: List[str], extracted_data: Dict
requires_human_review: bool, processing_time: float
```

### LangGraph Workflow Flow
```
[START] -> [anomaly_detection] -> [optimization_recommendation] -> route_after_optimization()
  If hitl_required: -> [hitl_checkpoint] -> route_after_hitl()
    If pending_review: -> END (pauses)
    If human_decision: -> [forecasting] -> [gamification] -> END
  Else: -> [forecasting] -> [gamification] -> END
```

### HITL Trigger Conditions (set by optimization agent)
- confidence < 0.60 -> "low_confidence"
- risk_level == "high" -> "high_risk_action"
- total_savings > $2000 -> "high_savings"

### Mock Analysis Issue
`_mock_analysis()` in main.py line 692 returns `"agent_decisions": []` (empty). Must be fixed to return realistic decisions.

### Existing Endpoints
```
POST /api/auth/login, GET /api/auth/me
GET /api/subscriptions, GET /api/subscriptions/{sub_id}
POST /api/subscriptions/{sub_id}/analyze
GET /api/recommendations, GET /api/recommendations/pending
POST /api/recommendations/{rec_id}/approve, POST /api/recommendations/{rec_id}/reject
GET /api/hitl/queue, POST /api/hitl/review/{analysis_id}
GET /api/forecasts/{sub_id}, GET /api/forecasts
GET /api/gamification/leaderboard, GET /api/gamification/my-stats
GET /api/gamification/badges, POST /api/gamification/awards, GET /api/gamification/awards
GET /api/analytics/cost-trends, GET /api/analytics/health-scores, GET /api/analytics/summary
```

### HITL Queue (in-memory dict in main.py)
```python
hitl_queue: Dict[str, Dict] = {}  # key=analysis_id
# Entry shape: analysis_id, subscription_id, subscription_name, recommendations,
#              priority, trigger_reasons, overall_confidence, total_potential_savings, created_at
```

---

## KEY FRONTEND DETAILS

### Zustand Stores
```js
// useAuthStore: user, token, isAuthenticated, setAuth(), logout()
// useAppStore: subscriptions, recommendations, hitlQueue, forecasts,
//              leaderboard, myStats, summary, loading, error, analysisInProgress
//              + setter for each
```

### API Service (api.js)
- Axios with baseURL '/api', JWT bearer token interceptor
- Handles 401 -> auto logout + redirect to /login
- All endpoints exported as named functions

### Current Routes (App.jsx)
```
/login -> LoginPage
/ -> Dashboard (protected)
/recommendations -> Recommendations (protected)
/forecasting -> Forecasting (protected)
/gamification -> Gamification (protected)
/subscriptions/:id -> SubscriptionDetail (protected)
```

### Sidebar Nav Items (Layout.jsx)
```js
[Dashboard (/), Recommendations (/recommendations), Forecasting (/forecasting), Gamification (/gamification)]
// DRAWER_WIDTH = 240
```

### Dashboard handleAnalyze (current)
- Calls `analyzeSubscription(subId)` -> shows snackbar with results
- Just a spinner on the button, no workflow visibility

### SubscriptionDetail handleAnalyze (current)
- Same pattern, plus a FAB button at bottom-right (will conflict with chat FAB)

---

## FILES TO CREATE (6)

| File | Feature |
|------|---------|
| `frontend/src/components/AgentWorkflowTracker/AgentWorkflowTracker.jsx` | F1 - Live pipeline drawer |
| `frontend/src/components/AgentReview/AgentReview.jsx` | F2 - HITL review page |
| `frontend/src/components/ChatWidget/ChatWidget.jsx` | F3 - Floating AI chat |
| `frontend/src/components/AgentReasoningPanel/AgentReasoningPanel.jsx` | F4 - Reusable "Why?" panel |
| `frontend/src/components/HealthScoreBreakdown/HealthScoreBreakdown.jsx` | F4 - Health score breakdown |
| `frontend/src/components/AgentDecisionTimeline/AgentDecisionTimeline.jsx` | F1+F2 - Shared timeline |

## FILES TO MODIFY (9)

| File | Changes |
|------|---------|
| `backend/main.py` | Add SSE streaming endpoint, chat endpoint, analysis detail endpoint, enrich HITL queue, fix mock agent_decisions, add ChatRequest model |
| `backend/src/agents/workflow.py` | Add `process_subscription_analysis_with_callbacks` using `workflow.stream()` |
| `frontend/src/App.jsx` | Add `/agent-review` route |
| `frontend/src/components/Layout/Layout.jsx` | Add "Agent Review" nav item with badge, mount ChatWidget |
| `frontend/src/components/Dashboard/Dashboard.jsx` | Open AgentWorkflowTracker on analyze |
| `frontend/src/components/SubscriptionDetail/SubscriptionDetail.jsx` | Open AgentWorkflowTracker, move FAB to avoid chat conflict |
| `frontend/src/components/Recommendations/Recommendations.jsx` | Add expandable reasoning rows |
| `frontend/src/services/api.js` | Add `analyzeSubscriptionStream`, `getAnalysis`, `chat` functions |
| `frontend/src/store/store.js` | Add `lastAnalysisResult`, `agentDecisions` to app store |

## NEW BACKEND ENDPOINTS (3)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/subscriptions/{sub_id}/analyze-stream` | SSE streaming analysis with per-agent progress |
| `GET` | `/api/analyses/{analysis_id}` | Full analysis details including agent_decisions |
| `POST` | `/api/chat` | Conversational AI chat |

---

## IMPLEMENTATION ORDER

### Phase 1: Backend Foundation
1. Fix `_mock_analysis` in main.py to generate realistic `agent_decisions` (line 692 currently `[]`)
2. Add `GET /api/analyses/{analysis_id}` endpoint
3. Add `_mock_analysis_with_callbacks()` with time.sleep delays for streaming
4. Add SSE endpoint `POST /api/subscriptions/{sub_id}/analyze-stream`
5. Add `process_subscription_analysis_with_callbacks` in workflow.py using `workflow.stream()`
6. Enrich HITL queue entries with `agent_decisions` and `anomalies`
7. Add `POST /api/chat` with Gemini + fallback
8. Add `ChatRequest` pydantic model

### Phase 2: Frontend - Workflow Tracker (F1)
1. Create `AgentDecisionTimeline.jsx`
2. Create `AgentWorkflowTracker.jsx` (uses fetch + ReadableStream for SSE, MUI Drawer + Stepper)
3. Update `api.js` with new functions
4. Update `store.js` with new state
5. Update `Dashboard.jsx` to open tracker on analyze
6. Update `SubscriptionDetail.jsx` to open tracker on analyze

### Phase 3: Frontend - HITL Review (F2) + Explainability (F4)
1. Create `AgentReasoningPanel.jsx`
2. Create `HealthScoreBreakdown.jsx`
3. Create `AgentReview.jsx` page
4. Update `Layout.jsx` with Agent Review nav item + pending count badge
5. Update `App.jsx` with `/agent-review` route
6. Update `Recommendations.jsx` with expandable reasoning

### Phase 4: Frontend - Chat Widget (F3)
1. Create `ChatWidget.jsx` (FAB + fixed-position panel)
2. Mount in `Layout.jsx`

---

## IMPORTANT TECHNICAL NOTES

1. **SSE with POST**: Browser EventSource API is GET-only. Use `fetch()` with `ReadableStream` to consume POST SSE.
2. **LangGraph .stream()**: Returns `{node_name: state_update}` dicts per node. Zero changes to agents.py needed.
3. **Mock streaming**: Use `time.sleep()` delays between agent events for demo without Gemini API key.
4. **Chat context**: Truncate DB context to ~6000 chars for Gemini prompt. Fallback handles common questions.
5. **SubscriptionDetail FAB conflict**: Move analyze FAB position to avoid overlap with chat FAB.
6. **No new dependencies needed**: All features use existing MUI components and FastAPI capabilities.
7. **HITL queue is in-memory**: Restarts clear it. Run analyses before demo.

---

## CURRENT PROGRESS

- [x] Plan approved
- [x] All source files read and understood
- [x] Phase 1: Backend changes - COMPLETE
  - Fixed `_mock_analysis` to generate realistic `agent_decisions` (was returning `[]`)
  - Added `_save_analysis_results` helper
  - Added SSE streaming endpoint `POST /api/subscriptions/{sub_id}/analyze-stream`
  - Added `_mock_analysis_with_callbacks` for per-agent streaming events
  - Added `GET /api/analyses/{analysis_id}` endpoint
  - Added `POST /api/chat` with Gemini LLM + rule-based fallback
  - Enriched HITL queue with `agent_decisions`, `anomalies`, `health_score`
- [x] Phase 2: Frontend workflow tracker - COMPLETE
  - Created `AgentDecisionTimeline.jsx`
  - Created `AgentWorkflowTracker.jsx` (SSE consumer + animated drawer)
  - Updated `api.js` with `getAnalysis`, `sendChatMessage`
  - Updated `store.js` with `lastAnalysisResult`
  - Updated `Dashboard.jsx` with tracker integration
  - Updated `SubscriptionDetail.jsx` with tracker + HealthScoreBreakdown
- [x] Phase 3: Frontend HITL review + explainability - COMPLETE
  - Created `AgentReasoningPanel.jsx`
  - Created `HealthScoreBreakdown.jsx`
  - Created `AgentReview.jsx` (full HITL review page)
  - Updated `Layout.jsx` with Agent Review nav + HITL badge
  - Updated `App.jsx` with `/agent-review` route
  - Updated `Recommendations.jsx` with expandable reasoning rows
- [x] Phase 4: Frontend chat widget - COMPLETE
  - Created `ChatWidget.jsx` (floating FAB + chat panel)
  - Mounted in `Layout.jsx`
- [x] Frontend build verified (12,383 modules, builds successfully)
- [x] Backend syntax verified (py_compile passes)

---

## VERIFICATION PLAN
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Login as `admin` / `admin123`
4. **F1**: Click "Run Analysis" -> drawer shows agents completing one-by-one
5. **F2**: Navigate to "Agent Review" -> see pending HITL items with timeline
6. **F3**: Click chat FAB -> ask "What's my highest spending subscription?"
7. **F4**: On Recommendations page, click "Why?" on any row
