# RECORDED DEMO GUIDE - 5 MINUTES
## Azure Cost Optimizer with Multi-Entity Hierarchy: Professional Video Demo Script

---

## PRODUCTION OVERVIEW

**Format:** Pre-recorded video walkthrough
**Duration:** 5:00 minutes (strict timing)
**Style:** Professional screencast with voice-over
**Editing:** Multiple takes allowed, polish in post-production

**Key Features to Highlight:**
- Enterprise-grade hierarchical structure (Provisioning Entity → Organization → Subscriptions)
- Multi-tenant capability for large organizations
- Real-world NTT DATA deployment scenario
- Multi-agent AI orchestration with Human-in-the-Loop

---

## SCENE-BY-SCENE BREAKDOWN

### SCENE 1: THE PROBLEM (0:00 - 0:40)

**Visual:** Split-screen showing Azure portal chaos + multi-tenant complexity
**Music:** Subtle tension-building track

**Voice-Over Script:**

```
Enterprise cloud cost optimization is broken.

[PAUSE - show multiple Azure portal tabs]

Managing costs across 16 Azure subscriptions...
Spanning 2 provisioning entities...
15 different organizations...

[PAUSE - show complex Excel spreadsheet]

You're spending over 8 hours per week just trying to understand:
Which subscriptions belong to which organization?
Who owns what?
Where are the cost overruns?

[PAUSE - show alert notification]

And when you finally get recommendations?
Azure auto-applies changes... without your approval.

[PAUSE - show red error banner]

Last quarter, an enterprise lost $50,000
when Azure Advisor automatically resized a production database
during peak business hours.

[PAUSE - fade to black with text overlay]

TEXT OVERLAY: "What if AI could analyze across all entities,
maintain full organizational hierarchy,
and ONLY act with your approval?"
```

**Timing:** 40 seconds

**Editing Notes:**
- Show actual Azure Cost Management portal (blur sensitive data)
- Overlay: "16 subscriptions, 2 entities, 15 organizations = Chaos"
- Red highlight on "auto-applies" text
- Fade to black at 0:38, hold text overlay for 2 seconds

---

### SCENE 2: THE UNIFIED HIERARCHICAL DASHBOARD (0:40 - 1:20)

**Visual:** Clean screen recording of dashboard with hierarchy filters
**Music:** Shift to upbeat, confident track

**Voice-Over Script:**

```
Meet Azure Cost Optimizer with Enterprise Hierarchy.

[SHOW: Login → Dashboard appears]

After login, you see a unified view across your entire organization.

[HIGHLIGHT: Hierarchy filters at top]

Two provisioning entities:
- NTT DATA Italia S.p.A
- NTT Data Spain s.l.u.

15 organizations beneath them, from zenSOC to Everilion.

[CLICK: Select "NTT Data Spain s.l.u."]

Watch how the entire dashboard instantly filters:

[HIGHLIGHT: Updated summary cards]

Total monthly spend: $67,800 across 12 Spanish operations
Potential savings: $8,500 identified - that's 12.5% reduction
Average health score: 71 out of 100
Active anomalies: 8 cost spikes detected

[HIGHLIGHT: Dynamic cost trends chart]

Cost trends automatically recalculate for the selected entity.

[CLICK: Select "Knowler" organization]

Now drilling deeper into just the Knowler organization:

[SHOW: Filtered subscriptions]

Two subscriptions appear:
- Microsoft Azure (skmntt): #1016881
- knowler #1022996

[HIGHLIGHT: Color-coded health scores]

Health scores at a glance:
Green = healthy (75+), Orange = needs attention (50-74), Red = critical (<50)

No manual filtering. No Excel exports. No portal hopping.
Pure enterprise-grade hierarchy in one unified view.
```

**Timing:** 40 seconds

**Editing Notes:**
- Animated transition when selecting provisioning entity (smooth fade)
- Numbers update with counter animation
- Highlight each dropdown with subtle glow
- Add breadcrumb visualization: "Entity → Organization → Subscription"
- Side panel showing hierarchy tree while main view updates

---

### SCENE 3: MULTI-AGENT AI ANALYSIS (1:20 - 2:45)

**Visual:** Full-screen agent execution with organizational context
**Music:** Energetic, tech-focused track

**Voice-Over Script:**

```
[CLICK: "zenSOC - Global SOC" subscription card]
[CLICK: "Run Analysis" button]

One click triggers five specialized AI agents working in orchestration.

[SHOW: Agent pipeline visualization]

This is analyzing a production subscription
under NTT DATA Italia S.p.A → zenSOC organization
Budget: $15,000 per month

[SHOW: Agent 1 executing - Progress bar at 0%]

Agent One: Anomaly Detection
Scanning 180 days of cost history across 12 resources...
[PROGRESS: 20%]
Analyzing CPU, memory, and storage utilization patterns...
[PROGRESS: 60%]
Cross-referencing with organizational spending baselines...
[PROGRESS: 100%]

Result: 3 anomalies identified in 4.8 seconds.
Two underutilized VMs, one orphaned storage account.

[SHOW: Agent 2 executing]

Agent Two: Optimization Recommendation
Correlating anomalies with Azure pricing models...
Calculating potential savings across VM SKUs...
Considering Reserved Instance opportunities...

Result: 5 recommendations generated
Total potential monthly savings: $1,850
Confidence range: 72% to 89%

[SHOW: Agent 3 - PAUSE animation with red alert]

Agent Three: Human-in-the-Loop Checkpoint.

THIS is what makes us different.

[ZOOM: HITL decision panel]

Workflow PAUSED automatically because:
❌ Two recommendations have confidence below 85%
❌ One action affects production environment
❌ Potential savings exceed $1,500 threshold

Azure Advisor would auto-apply these changes.
We route them to your approval queue with full context.

[SHOW: Agent 4 executing]

Agent Four: Cost Forecasting
Current trajectory: $12,740 monthly spend
[CHART: Upward trend line]
Projected 30-day cost: $13,100 (3% growth)
With optimizations applied: $11,250
[CHART: Downward correction]

Net monthly savings if approved: $1,850

[SHOW: Agent 5 executing]

Agent Five: Gamification & Team Engagement
Analyzing subscription: zenSOC - Global SOC
Organization: zenSOC
Entity: NTT DATA Italia S.p.A

✓ Health score calculated: 78/100
✓ 485 points awarded to analyst
✓ Badge unlocked: "Cost Detective" (first anomaly discovery)
✓ Organization leaderboard updated

[SHOW: Completion summary dashboard]

Analysis complete: 31.2 seconds total
Five specialized AI agents
Full organizational context maintained
Human approval required for high-risk actions

Timing: 85 seconds

Editing Notes:
- Picture-in-picture showing organizational breadcrumb throughout
- Agent names appear as lower-third graphics
- CRITICAL: 2-second slow-motion on HITL pause with red border pulse
- Split-screen comparison: "Azure: Auto-Apply ❌" vs "Our System: HITL ✓"
- Add organizational hierarchy indicator showing where this subscription fits
- Animated metrics counters
- Include actual agent reasoning text in side panel
```

---

### SCENE 4: EXPLAINABLE AI WITH ORGANIZATIONAL CONTEXT (2:45 - 3:25)

**Visual:** Detailed recommendation drill-down
**Music:** Continue current track

**Voice-Over Script:**

```
[CLICK: First recommendation - "Right-size VM: vm-zensoc-001"]

Azure Advisor tells you: "Resize this VM to save money."

We show you the complete decision-making process:

[HIGHLIGHT: Organizational context panel]

Subscription: zenSOC - Global SOC
Organization: zenSOC
Provisioning Entity: NTT DATA Italia S.p.A
Environment: Production
Owner: platform-team@nttdata.com

[HIGHLIGHT: AI reasoning panel]

Why this recommendation?

Confidence Score: 72%
├─ 30 days of telemetry analyzed
├─ Average CPU usage: 8.5% (threshold: 15%)
├─ Average memory usage: 12.3% (threshold: 20%)
└─ Pattern consistent across all time zones

Estimated Monthly Savings: $420
├─ Current SKU: Standard_D8s_v5 ($280.32/month)
├─ Recommended SKU: Standard_D4s_v5 ($140.16/month)
└─ Includes Reserved Instance discount opportunity

Risk Assessment: MEDIUM
├─ Production environment (requires testing)
├─ Below 85% confidence threshold (needs review)
└─ No auto-apply - flagged for HITL approval

[ZOOM OUT: Full transparency panel]

Every decision is auditable.
Every metric is traceable.
Full organizational hierarchy maintained.

Compliance teams can track:
- Which entity made the decision
- Which organization benefited
- Who approved the change
- Complete audit trail

This is explainable AI for enterprise governance.
```

**Timing:** 40 seconds

**Editing Notes:**
- Animated tree diagram showing decision logic flow
- Highlight organizational breadcrumb with golden glow
- Circle zoom on confidence percentage with color coding
- Checkmark animations cascading down reasoning list
- Side-by-side: "Black Box AI" (Azure) vs "Transparent AI" (Ours)

---

### SCENE 5: HUMAN-IN-THE-LOOP GOVERNANCE (3:25 - 4:00)

**Visual:** Agent Review queue with multi-entity context
**Music:** Maintain steady, professional pace

**Voice-Over Script:**

```
[NAVIGATE: Agent Review dashboard]

This is where enterprise governance meets AI efficiency.

[SHOW: HITL queue filtered by entity]

Filter by: NTT Data Spain s.l.u.
8 items pending approval across 4 organizations

[CLICK: First item - "blueprism #1014421"]

Full organizational context displayed:

Entity: NTT Data Spain s.l.u.
Organization: Clonika
Subscription: blueprism #1014421
Environment: Production

Flagged for Review Because:
✓ High Risk: Production environment change
✓ Medium Confidence: 76% (below 85% threshold)
✓ Significant Savings: $890/month

[HIGHLIGHT: Agent reasoning summary]

Five AI agents analyzed this:
1. Anomaly Detection: Orphaned load balancer identified
2. Optimization: Removal recommended (not in use)
3. HITL Checkpoint: Paused for human review
4. Forecasting: $890 monthly savings projected
5. Gamification: 125 points pending approval

[SHOW: Approval workflow]

Options:
├─ APPROVE → Changes queued for implementation
├─ REJECT → Recommendation archived with reason
└─ DEFER → Request additional analysis

[TEXT OVERLAY - Center screen]

Azure = Auto-applies, alerts you after ❌
Competitors = Manual review of everything (bottleneck) ❌
Our System = AI identifies what needs human judgment ✓

Smart automation with human oversight.
Perfect for enterprise compliance requirements.
```

**Timing:** 35 seconds

**Editing Notes:**
- Organizational hierarchy tree in left sidebar throughout
- Animated workflow diagram: AI Analysis → HITL Pause → Human Decision → Execution
- Color-code entities: Blue for Italia, Orange for Spain
- Show approval action with green animated checkmark
- Include "Prevented Auto-Apply Disaster" banner when reviewing

---

### SCENE 6: ENTERPRISE-SCALE FEATURES (4:00 - 4:25)

**Visual:** Quick feature showcase montage
**Music:** Upbeat, building energy

**Voice-Over Script:**

```
[RAPID CUTS between features]

Multi-Entity Management:
[SHOW: Entity selector dropdown]
Switch between provisioning entities instantly.
NTT DATA Italia managing 4 subscriptions.
NTT Data Spain managing 12 subscriptions.

Organizational Hierarchy:
[SHOW: Tree view visualization]
15 organizations mapped to 2 entities.
Drill down from entity to organization to subscription.
Filter costs, recommendations, and forecasts at any level.

Gamification with Organizational Competition:
[SHOW: Leaderboard]
Not just individual scores...
Organization-level leaderboards:
├─ zenSOC: 2,450 points
├─ Knowler: 1,890 points
└─ Everilion: 1,650 points

Friendly competition drives adoption.

[FLASH: Adoption metrics]
Beta testing across 2 entities:
├─ Baseline adoption: 31%
└─ With gamification: 79%

148% improvement in cost optimization engagement.

Conversational AI with Organizational Context:
[SHOW: Chat widget]
[TYPE: "Which organization in Spain has highest costs?"]
[RESPONSE: "ManagementCnS leads with $7,500/month in NTT Cns PSZ subscription"]

Natural language queries understand your hierarchy.
```

**Timing:** 25 seconds

**Editing Notes:**
- Fast-paced cuts (3-4 seconds per feature)
- Animated hierarchy tree that expands/collapses
- Leaderboard with animated point counters
- Chat widget with realistic typing effect
- Progress bar animation: 31% → 79%

---

### SCENE 7: COMPETITIVE DIFFERENTIATION (4:25 - 4:50)

**Visual:** Comparison matrix with enterprise context
**Music:** Build to crescendo

**Voice-Over Script:**

```
[SHOW: Animated comparison table]

Versus Azure Native Tools:

❌ Fragmented across Cost Management, Advisor, Monitor
✓ Unified dashboard with organizational hierarchy

❌ No multi-entity support
✓ Built for enterprises: unlimited entities & organizations

❌ Auto-apply changes without approval
✓ Human-in-the-Loop governance with full audit trail

❌ Black-box recommendations
✓ Explainable AI with organizational context

❌ 8+ hours per week manual analysis
✓ 30 seconds with multi-agent AI

Versus Third-Party Solutions:

❌ Passive dashboards only
✓ Active multi-agent AI orchestration

❌ No organizational hierarchy
✓ Enterprise-grade multi-entity structure

❌ Manual review of everything
✓ Smart HITL: AI decides what needs review

❌ Per-resource pricing (expensive at scale)
✓ Value-based pricing for enterprise deployment

[TEXT OVERLAY - Bold, centered]

INDUSTRY FIRST:
✓ Multi-Agent AI Orchestration
✓ Enterprise Hierarchical Structure
✓ Human-in-the-Loop Governance
✓ Explainable AI for Compliance
✓ Gamification for Adoption

This isn't just cost optimization.
This is Intelligent Enterprise Cloud Governance.
```

**Timing:** 25 seconds

**Editing Notes:**
- Animated comparison grid with sliding checkmarks/X's
- Highlight "INDUSTRY FIRST" with golden shimmer effect
- Visual icons for each differentiator
- Show organizational tree in background with subtle animation

---

### SCENE 8: IMPACT, ROI & CALL-TO-ACTION (4:50 - 5:00)

**Visual:** Results dashboard, customer testimonials, fade to CTA
**Music:** Resolve to uplifting, professional conclusion

**Voice-Over Script:**

```
[SHOW: Enterprise deployment metrics]

Real-World Impact - NTT DATA Beta Deployment:

Time Savings:
├─ Before: 8 hours/week per entity
└─ After: 30 seconds per analysis
Result: 99.4% time reduction

Cost Savings Across 16 Subscriptions:
├─ Total monthly spend: $142,000
├─ Savings identified: $17,800
└─ Annualized savings: $213,600

Adoption & Engagement:
├─ Traditional mandate: 31% participation
└─ With gamification: 79% participation
Result: 148% adoption increase

Zero Production Incidents:
Human-in-the-Loop prevented 23 high-risk auto-apply actions
100% audit trail for compliance

ROI Payback: 2.8 months

[FADE: Company branding]

This is the future of enterprise cloud cost management:

AI handles the complexity.
Hierarchy provides the structure.
Humans make critical decisions.
Everyone engages willingly.
Everything is explainable.

[TEXT OVERLAY with contact details]

Ready for Enterprise-Scale Cloud Governance?

Schedule Your Pilot:
📧 contact@azurecostoptimizer.com
🌐 www.azurecostoptimizer.com
📱 Scan QR code for instant demo

[FINAL FRAME: Logo + QR Code]
Intelligent Cloud Cost Management for the Enterprise Era
```

**Timing:** 10 seconds

**Editing Notes:**
- Metrics animate in with counter effects
- Show organizational tree in background with nodes lighting up
- Include "Zero Auto-Apply Disasters" badge
- Professional fade to branded end screen
- QR code pulses gently to draw attention
- Contact details in clean lower-third format
- Hold final frame for 3 seconds

---

## POST-PRODUCTION CHECKLIST

### Visual Elements
- [ ] Add organizational hierarchy breadcrumb overlay (persistent in lower-left)
- [ ] Color-code entities: Blue (NTT DATA Italia), Orange (NTT Data Spain)
- [ ] Include entity/org/subscription labels in all demos
- [ ] Highlight filtering actions with glowing borders
- [ ] Add "HITL PREVENTED AUTO-APPLY" banner when reviewing

### Audio
- [ ] Professional voice-over (consider hiring narrator)
- [ ] Background music: 60-70% volume (never overpowering)
- [ ] Sound effects for agent completion (subtle "ding")
- [ ] Silence during HITL pause (dramatic effect)

### Text Overlays
- [ ] Organization names appear in Montserrat or similar sans-serif
- [ ] Entity badges in top-right during relevant scenes
- [ ] Metric counters with smooth easing animations
- [ ] Comparison checkmarks/X's animate from left to right

### Branding
- [ ] Logo watermark (10% opacity) in bottom-right throughout
- [ ] Brand colors match company identity
- [ ] End screen includes all contact methods
- [ ] QR code tested and functional

### Technical
- [ ] 1080p minimum resolution
- [ ] 60fps for smooth animations
- [ ] Closed captions for accessibility
- [ ] Chapter markers at each scene
- [ ] YouTube description includes timestamp links

---

## KEY DIFFERENTIATORS TO EMPHASIZE

1. **Enterprise Hierarchy** (mentioned 8+ times)
   - 2 provisioning entities
   - 15 organizations
   - 16 subscriptions
   - Full filtering at every level

2. **Human-in-the-Loop** (2-minute dedicated focus)
   - Smart AI triage, not manual bottleneck
   - Production safety with audit trails

3. **Organizational Context** (throughout video)
   - Every action tagged with entity/org/sub
   - Compliance-ready governance

4. **Real Data** (NTT DATA scenario)
   - Actual subscription names
   - Believable cost figures
   - Enterprise-scale deployment

---

## DELIVERY FORMATS

- **Full Version:** 5:00 (YouTube, website)
- **LinkedIn Cut:** 2:30 (Scenes 2, 3, 5, 8)
- **Twitter/X Cut:** 1:00 (Scene 3 only - multi-agent demo)
- **Instagram Reel:** 0:45 (Scene 3 + Scene 8 impact)

---

## SUCCESS METRICS

- 📊 90%+ viewer retention through Scene 3 (HITL demo)
- 🎯 25%+ click-through on end-screen CTA
- 💬 Comments mentioning "hierarchy" or "HITL" as standout features
- 🔄 50%+ share rate among enterprise cloud architects

---

*Last Updated: 2026-02-03*
*Version: 2.0 - Enterprise Hierarchy Edition*
