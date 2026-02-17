import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Drawer, Box, Typography, IconButton, LinearProgress, Chip, Collapse,
  Paper, Button, Divider, CircularProgress, Card, CardContent,
} from '@mui/material';
import {
  Close, BugReport, Lightbulb, Gavel, TrendingUp, EmojiEvents,
  CheckCircle, HourglassTop, RadioButtonUnchecked, ExpandMore, ExpandLess,
  SmartToy, Speed, Visibility, VisibilityOff,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import CountUp from 'react-countup';

const AGENT_STEPS = [
  { key: 'anomaly_detection', name: 'Anomaly Detection Agent', icon: <BugReport />, color: '#d32f2f', description: 'Scanning resources for cost anomalies' },
  { key: 'optimization_recommendation', name: 'Optimization Recommendation Agent', icon: <Lightbulb />, color: '#0078d4', description: 'Generating cost-saving recommendations' },
  { key: 'hitl_checkpoint', name: 'HITL Checkpoint Agent', icon: <Gavel />, color: '#ed6c02', description: 'Evaluating if human review is needed' },
  { key: 'forecasting', name: 'Forecasting Agent', icon: <TrendingUp />, color: '#7b1fa2', description: 'Projecting future costs' },
  { key: 'gamification', name: 'Gamification Agent', icon: <EmojiEvents />, color: '#2e7d32', description: 'Calculating health score and rewards' },
];

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

// Global lock to prevent duplicate analysis runs across all component instances
const globalAnalysisLocks = new Map();

export default function AgentWorkflowTracker({ open, onClose, subscriptionId, subscriptionName, onComplete, onViewResults }) {
  const [agents, setAgents] = useState(AGENT_STEPS.map((a) => ({ ...a, status: 'pending', decision: null })));
  const [pipelineStatus, setPipelineStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [showDetails, setShowDetails] = useState(true); // NEW: Progressive disclosure
  const abortRef = useRef(null);
  const runningRef = useRef(false);

  const completedCount = agents.filter((a) => a.status === 'completed').length;
  const progress = (completedCount / agents.length) * 100;

  useEffect(() => {
    if (!open || !subscriptionId) return;

    // Prevent duplicate runs using global lock
    if (globalAnalysisLocks.get(subscriptionId)) {
      console.log('[AgentWorkflowTracker] Analysis already running for subscription:', subscriptionId);
      return;
    }

    console.log('[AgentWorkflowTracker] Starting analysis for subscription:', subscriptionId);
    globalAnalysisLocks.set(subscriptionId, true);
    runningRef.current = true;

    // Reset state inline to avoid dependency issues
    setAgents(AGENT_STEPS.map((a) => ({ ...a, status: 'pending', decision: null })));
    setPipelineStatus('running');
    setResult(null);
    setExpandedAgent(null);

    const token = localStorage.getItem('token');
    const controller = new AbortController();
    abortRef.current = controller;

    (async () => {
      try {
        const response = await fetch(`/api/subscriptions/${subscriptionId}/analyze-stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ analysis_period: '30d' }),
          signal: controller.signal,
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          let currentEventType = null;
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEventType = line.slice(7).trim();
            } else if (line.startsWith('data: ') && currentEventType) {
              try {
                const data = JSON.parse(line.slice(6));
                handleSSEEvent(currentEventType, data);
              } catch (e) { /* skip malformed */ }
              currentEventType = null;
            }
          }
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('[AgentWorkflowTracker] Fetch error:', err);
          setPipelineStatus('error');
          runningRef.current = false;
          globalAnalysisLocks.delete(subscriptionId);
        }
      }
    })();

    return () => {
      console.log('[AgentWorkflowTracker] Cleanup for subscription:', subscriptionId);
      controller.abort();
      runningRef.current = false;
      globalAnalysisLocks.delete(subscriptionId);
    };
  }, [open, subscriptionId]);

  const handleSSEEvent = (eventType, data) => {
    switch (eventType) {
      case 'agent_start':
        setAgents((prev) =>
          prev.map((a) => a.key === data.agent_key ? { ...a, status: 'running' } : a)
        );
        setExpandedAgent(data.agent_key);
        break;

      case 'agent_complete':
        setAgents((prev) =>
          prev.map((a) => a.key === data.agent_key ? { ...a, status: 'completed', decision: data.decision } : a)
        );
        break;

      case 'complete':
        setPipelineStatus('completed');
        setResult(data);
        runningRef.current = false;
        globalAnalysisLocks.delete(subscriptionId);
        console.log('[AgentWorkflowTracker] Analysis completed for subscription:', subscriptionId);
        if (onComplete) onComplete(data);
        break;

      case 'error':
        setPipelineStatus('error');
        runningRef.current = false;
        globalAnalysisLocks.delete(subscriptionId);
        console.log('[AgentWorkflowTracker] Analysis error for subscription:', subscriptionId);
        break;
    }
  };

  const handleClose = () => {
    if (abortRef.current && pipelineStatus === 'running') {
      abortRef.current.abort();
    }
    onClose();
  };

  const getStepIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle sx={{ color: '#2e7d32', fontSize: 22 }} />;
      case 'running': return <CircularProgress size={20} thickness={5} />;
      default: return <RadioButtonUnchecked sx={{ color: '#bdbdbd', fontSize: 22 }} />;
    }
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={handleClose}
      PaperProps={{
        sx: { width: { xs: '100%', sm: 520 }, bgcolor: '#fafafa' },
      }}
    >
      {/* Header */}
      <Box sx={{
        px: 3, py: 2,
        background: 'linear-gradient(135deg, #0a1929, #0d2744)',
        color: '#fff',
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToy sx={{ color: '#50e6ff' }} />
            <Typography variant="h6" fontWeight={700}>AI Agent Pipeline</Typography>
          </Box>
          <IconButton onClick={handleClose} sx={{ color: '#fff' }}>
            <Close />
          </IconButton>
        </Box>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mt: 0.5 }}>
          {subscriptionName}
        </Typography>

        {/* Progress bar */}
        <Box sx={{ mt: 2, mb: 0.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              {pipelineStatus === 'completed' ? 'Analysis Complete' :
               pipelineStatus === 'error' ? 'Error Occurred' :
               `Processing... ${completedCount}/${agents.length} agents`}
            </Typography>
            <Typography variant="caption" sx={{ color: '#50e6ff' }}>
              {Math.round(progress)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 6, borderRadius: 3,
              bgcolor: 'rgba(255,255,255,0.15)',
              '& .MuiLinearProgress-bar': {
                bgcolor: pipelineStatus === 'error' ? '#d32f2f' : '#50e6ff',
                borderRadius: 3,
                transition: 'transform 0.8s ease-in-out',
              },
            }}
          />
        </Box>
      </Box>

      {/* NEW: Quick Summary Card (Progressive Disclosure) */}
      {!showDetails && pipelineStatus !== 'idle' && (
        <Box sx={{ p: 2 }}>
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ bgcolor: '#f0f7ff', border: '2px solid #0078d4' }}>
              <CardContent>
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  Quick Summary
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {agents.map((agent) => (
                    <Box key={agent.key} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStepIcon(agent.status)}
                      <Typography variant="body2" sx={{ flex: 1 }}>
                        {agent.name}
                      </Typography>
                      {agent.status === 'completed' && agent.decision && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", stiffness: 200 }}
                        >
                          <CheckCircle sx={{ color: '#2e7d32', fontSize: 20 }} />
                        </motion.div>
                      )}
                    </Box>
                  ))}
                </Box>
                {pipelineStatus === 'completed' && result && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #ddd' }}>
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                      Key Findings:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Chip label={`${result.anomaly_count} Anomalies`} size="small" />
                      <Chip label={`${result.recommendation_count} Recommendations`} size="small" color="primary" />
                      <Chip label={fmt(result.total_potential_savings) + '/mo savings'} size="small" color="success" />
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Visibility />}
              onClick={() => setShowDetails(true)}
              sx={{ mt: 1 }}
            >
              Show Full Agent Timeline
            </Button>
          </motion.div>
        </Box>
      )}

      {/* Toggle Button (when details are shown) */}
      {showDetails && pipelineStatus !== 'idle' && (
        <Box sx={{ px: 2, pt: 2 }}>
          <Button
            fullWidth
            size="small"
            variant="text"
            startIcon={<VisibilityOff />}
            onClick={() => setShowDetails(false)}
            sx={{ mb: 1 }}
          >
            Hide Details (Show Summary)
          </Button>
        </Box>
      )}

      {/* Agent Steps */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Collapse in={showDetails}>
          {agents.map((agent, idx) => {
          const isExpanded = expandedAgent === agent.key;
          const d = agent.decision;

          return (
            <Box key={agent.key} sx={{ mb: 1 }}>
              <Paper
                elevation={agent.status === 'running' ? 3 : agent.status === 'completed' ? 1 : 0}
                sx={{
                  borderRadius: 2,
                  overflow: 'hidden',
                  border: agent.status === 'running' ? `2px solid ${agent.color}` : '1px solid #e0e0e0',
                  transition: 'all 0.3s ease',
                  ...(agent.status === 'running' && {
                    animation: 'pulse 2s ease-in-out infinite',
                    '@keyframes pulse': {
                      '0%, 100%': { boxShadow: `0 0 0 0 ${agent.color}33` },
                      '50%': { boxShadow: `0 0 12px 4px ${agent.color}22` },
                    },
                  }),
                }}
              >
                {/* Agent header */}
                <Box
                  onClick={() => d && setExpandedAgent(isExpanded ? null : agent.key)}
                  sx={{
                    display: 'flex', alignItems: 'center', gap: 1.5, px: 2, py: 1.5,
                    cursor: d ? 'pointer' : 'default',
                    bgcolor: agent.status === 'completed' ? '#f8fdf8' : agent.status === 'running' ? '#fff' : '#fafafa',
                  }}
                >
                  {/* Step number + icon */}
                  <Box sx={{
                    width: 36, height: 36, borderRadius: '50%',
                    bgcolor: agent.status === 'pending' ? '#f5f5f5' : `${agent.color}15`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: agent.status === 'pending' ? '#bdbdbd' : agent.color,
                    flexShrink: 0,
                  }}>
                    {agent.icon}
                  </Box>

                  {/* Text */}
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="body2" fontWeight={600} sx={{
                      color: agent.status === 'pending' ? '#9e9e9e' : '#1a1a1a',
                    }}>
                      {agent.name}
                    </Typography>
                    <Typography variant="caption" sx={{
                      color: agent.status === 'pending' ? '#bdbdbd' : '#666',
                    }}>
                      {agent.status === 'running' ? agent.description :
                       agent.status === 'completed' && d ? d.decision : 'Waiting...'}
                    </Typography>
                  </Box>

                  {/* Status icon */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {d && d.processing_time && agent.status === 'completed' && (
                      <Chip icon={<Speed sx={{ fontSize: 14 }} />} label={`${d.processing_time.toFixed(1)}s`} size="small" variant="outlined" sx={{ height: 22, fontSize: 11 }} />
                    )}
                    {getStepIcon(agent.status)}
                    {d && (isExpanded ? <ExpandLess sx={{ color: '#999', fontSize: 18 }} /> : <ExpandMore sx={{ color: '#999', fontSize: 18 }} />)}
                  </Box>
                </Box>

                {/* Expanded details */}
                <Collapse in={isExpanded && !!d}>
                  {d && (
                    <Box sx={{ px: 2, pb: 2, pt: 0.5, borderTop: '1px solid #f0f0f0' }}>
                      {/* Confidence bar */}
                      {d.confidence != null && (
                        <Box sx={{ mb: 1.5 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">Confidence</Typography>
                            <Typography variant="caption" fontWeight={600}>
                              {Math.round(d.confidence * 100)}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={d.confidence * 100}
                            sx={{
                              height: 4, borderRadius: 2,
                              bgcolor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: d.confidence >= 0.85 ? '#2e7d32' : d.confidence >= 0.6 ? '#ed6c02' : '#d32f2f',
                                borderRadius: 2,
                              },
                            }}
                          />
                        </Box>
                      )}

                      {/* Reasoning */}
                      {d.reasoning && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, lineHeight: 1.6 }}>
                          {d.reasoning}
                        </Typography>
                      )}

                      {/* Flags */}
                      {d.flags && d.flags.length > 0 && (
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {d.flags.map((flag, fi) => (
                            <Chip
                              key={fi}
                              label={flag.replace(/_/g, ' ')}
                              size="small"
                              variant="outlined"
                              color={d.requires_human_review ? 'warning' : 'default'}
                              sx={{ height: 22, fontSize: 11 }}
                            />
                          ))}
                        </Box>
                      )}
                    </Box>
                  )}
                </Collapse>
              </Paper>

              {/* Connector line */}
              {idx < agents.length - 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 0.3 }}>
                  <Box sx={{
                    width: 2, height: 12,
                    bgcolor: agents[idx + 1].status !== 'pending' ? agent.color : '#e0e0e0',
                    transition: 'background-color 0.5s',
                  }} />
                </Box>
              )}
            </Box>
          );
        })}
        </Collapse>
      </Box>

      {/* Footer - Result summary */}
      {pipelineStatus === 'completed' && result && (
        <>
          <Divider />
          <Box sx={{ p: 2, bgcolor: '#f0f7ff' }}>
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1, color: '#0078d4' }}>
              Analysis Results
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box>
                <Typography variant="caption" color="text.secondary">Anomalies</Typography>
                <Typography variant="body2" fontWeight={700}>
                  <CountUp end={result.anomaly_count} duration={1} />
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Recommendations</Typography>
                <Typography variant="body2" fontWeight={700}>
                  <CountUp end={result.recommendation_count} duration={1} />
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Potential Savings</Typography>
                <Typography variant="body2" fontWeight={700} color="success.main">
                  $<CountUp end={result.total_potential_savings} duration={1.5} decimals={0} />/mo
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Health Score</Typography>
                <Typography variant="body2" fontWeight={700}>
                  <CountUp end={result.health_score} duration={1} />/100
                </Typography>
              </Box>
            </Box>
            {result.hitl_required && (
              <Chip label="Human Review Required" color="warning" size="small" sx={{ mt: 1 }} />
            )}
            <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={() => {
              if (onViewResults) {
                onViewResults(subscriptionId);
              } else {
                handleClose();
              }
            }}>
              View Results
            </Button>
          </Box>
        </>
      )}
    </Drawer>
  );
}
