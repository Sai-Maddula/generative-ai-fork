import { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Chip, Button, TextField,
  Checkbox, Alert, CircularProgress, Snackbar, Divider, Paper,
  Grid, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Gavel, Warning, CheckCircle, Cancel, TrendingDown, SmartToy,
} from '@mui/icons-material';
import { getHITLQueue, submitHITLReview, getProvisioningEntities, getOrganizations, getSubscriptions } from '../../services/api';
import AgentDecisionTimeline from '../AgentDecisionTimeline/AgentDecisionTimeline';
import { useAppStore } from '../../store/store';

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

const priorityColors = { critical: 'error', high: 'error', medium: 'warning', low: 'info' };

export default function AgentReview() {
  const {
    selectedProvider,
    selectedProvisioningEntity,
    selectedOrganization,
    selectedSubscription,
    setSelectedProvisioningEntity,
    setSelectedOrganization,
    setSelectedSubscription
  } = useAppStore();
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState({});
  const [selectedRecs, setSelectedRecs] = useState({});
  const [actionLoading, setActionLoading] = useState(null);
  const [snack, setSnack] = useState({ open: false, msg: '', severity: 'success' });
  const [provisioningEntities, setProvisioningEntities] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [subs, setSubs] = useState([]);

  useEffect(() => {
    loadHierarchy();
  }, [selectedProvider]);

  useEffect(() => {
    if (selectedProvider === 'azure' && selectedProvisioningEntity) {
      loadOrganizations(selectedProvisioningEntity);
    } else {
      setOrganizations([]);
    }
  }, [selectedProvider, selectedProvisioningEntity]);

  useEffect(() => {
    loadData();
  }, [selectedProvider, selectedProvisioningEntity, selectedOrganization, selectedSubscription]);

  const loadHierarchy = async () => {
    if (selectedProvider === 'azure') {
      try {
        const res = await getProvisioningEntities();
        setProvisioningEntities(res.data);
      } catch (err) {
        console.error('Failed to load provisioning entities:', err);
      }
    } else {
      setProvisioningEntities([]);
      setOrganizations([]);
    }
  };

  const loadOrganizations = async (entityId) => {
    try {
      const res = await getOrganizations(entityId);
      setOrganizations(res.data);
    } catch (err) {
      console.error('Failed to load organizations:', err);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [queueRes, subsRes] = await Promise.all([
        getHITLQueue(selectedProvider, selectedProvisioningEntity, selectedOrganization),
        getSubscriptions(selectedProvisioningEntity, selectedOrganization, selectedProvider)
      ]);
      setQueue(queueRes.data);
      setSubs(subsRes.data);
      // Initialize selections: all recommendations selected by default
      const selections = {};
      queueRes.data.forEach((entry) => {
        const recIds = {};
        (entry.recommendations || []).forEach((r) => { recIds[r.id] = true; });
        selections[entry.analysis_id] = recIds;
      });
      setSelectedRecs(selections);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleRec = (analysisId, recId) => {
    setSelectedRecs((prev) => ({
      ...prev,
      [analysisId]: {
        ...prev[analysisId],
        [recId]: !prev[analysisId]?.[recId],
      },
    }));
  };

  const handleReview = async (analysisId, decision) => {
    setActionLoading(analysisId);
    try {
      await submitHITLReview(analysisId, {
        decision,
        notes: notes[analysisId] || '',
      });
      setSnack({
        open: true,
        msg: `Analysis ${decision === 'approve' ? 'approved' : 'rejected'} successfully`,
        severity: decision === 'approve' ? 'success' : 'info',
      });
      loadData();
    } catch (err) {
      setSnack({ open: true, msg: 'Review submission failed', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
        <Gavel sx={{ color: '#0078d4', fontSize: 28 }} />
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.15rem' }}>Agent Review</Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '0.8rem' }}>
        Review AI agent decisions that require human oversight. Approve or reject recommendations before they are implemented.
      </Typography>

      {/* Hierarchy Filters */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Typography variant="body2" sx={{ mb: 2, fontWeight: 600, fontSize: '0.85rem' }}>
          Filter by Hierarchy
        </Typography>
        <Grid container spacing={2}>
          {selectedProvider === 'azure' && (
            <>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Provisioning Entity</InputLabel>
                  <Select
                    value={selectedProvisioningEntity || ''}
                    label="Provisioning Entity"
                    onChange={(e) => {
                      const val = e.target.value;
                      setSelectedProvisioningEntity(val === '' ? null : val);
                      setSelectedOrganization(null);
                      setSelectedSubscription(null);
                    }}
                  >
                    <MenuItem value="">All Entities</MenuItem>
                    {provisioningEntities.map((pe) => (
                      <MenuItem key={pe.id} value={pe.id}>
                        {pe.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small" disabled={!selectedProvisioningEntity}>
                  <InputLabel>Organization</InputLabel>
                  <Select
                    value={selectedOrganization || ''}
                    label="Organization"
                    onChange={(e) => {
                      const val = e.target.value;
                      setSelectedOrganization(val === '' ? null : val);
                      setSelectedSubscription(null);
                    }}
                  >
                    <MenuItem value="">All Organizations</MenuItem>
                    {organizations.map((org) => (
                      <MenuItem key={org.id} value={org.id}>
                        {org.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}
          <Grid item xs={12} sm={selectedProvider === 'azure' ? 4 : 12}>
            <FormControl fullWidth size="small">
              <InputLabel>Subscription</InputLabel>
              <Select
                value={selectedSubscription || ''}
                label="Subscription"
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedSubscription(val === '' ? null : val);
                }}
              >
                <MenuItem value="">All Subscriptions</MenuItem>
                {subs.filter(s => {
                  const subProvider = (s.provider || 'azure').toLowerCase();
                  return subProvider === selectedProvider;
                }).map((s) => (
                  <MenuItem key={s.id} value={s.id}>
                    {s.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Card>

      {queue.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <CheckCircle sx={{ fontSize: 48, color: '#2e7d32', mb: 2 }} />
            <Typography variant="h6" fontWeight={600} sx={{ fontSize: '1rem' }}>All Clear</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontSize: '0.85rem' }}>
              No analyses require human review. Run an analysis on a subscription to see agent decisions here.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {queue.map((entry) => {
            const recs = entry.recommendations || [];
            const decisions = entry.agent_decisions || [];
            const isProcessing = actionLoading === entry.analysis_id;

            return (
              <Card key={entry.analysis_id} sx={{ overflow: 'visible' }}>
                {/* Header */}
                <Box sx={{
                  px: 3, py: 2,
                  background: 'linear-gradient(135deg, #0a1929, #0d2744)',
                  color: '#fff',
                  borderRadius: '12px 12px 0 0',
                }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1rem' }}>{entry.subscription_name}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.7rem' }}>
                        Analysis: {entry.analysis_id?.slice(0, 8)}...
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip
                        label={`Priority: ${entry.priority}`}
                        color={priorityColors[entry.priority] || 'default'}
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                      <Chip
                        label={`${Math.round((entry.overall_confidence || 0) * 100)}% confidence`}
                        size="small"
                        sx={{ bgcolor: 'rgba(255,255,255,0.15)', color: '#fff' }}
                      />
                    </Box>
                  </Box>
                </Box>

                <CardContent sx={{ p: 3 }}>
                  {/* Why Review Needed */}
                  <Paper sx={{ p: 2, mb: 3, bgcolor: '#fff8e1', borderRadius: 2, border: '1px solid #ffe082' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Warning sx={{ color: '#f57f17', fontSize: 20 }} />
                      <Typography variant="subtitle2" fontWeight={700} sx={{ color: '#e65100' }}>
                        Why Human Review Is Required
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.75, flexWrap: 'wrap' }}>
                      {(entry.trigger_reasons || []).map((reason, i) => (
                        <Chip
                          key={i}
                          label={reason.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                          size="small"
                          color="warning"
                          variant="outlined"
                          sx={{ fontWeight: 500 }}
                        />
                      ))}
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      Total potential savings: <strong>{fmt(entry.total_potential_savings)}/mo</strong> |
                      {' '}Confidence: <strong>{Math.round((entry.overall_confidence || 0) * 100)}%</strong>
                    </Typography>
                  </Paper>

                  {/* Agent Decision Timeline */}
                  {decisions.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                        <SmartToy sx={{ color: '#0078d4', fontSize: 20 }} />
                        <Typography variant="subtitle2" fontWeight={700} sx={{ fontSize: '0.85rem' }}>Agent Decision Chain</Typography>
                      </Box>
                      <AgentDecisionTimeline decisions={decisions} compact />
                    </Box>
                  )}

                  <Divider sx={{ my: 2 }} />

                  {/* Recommendations to Review */}
                  <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5, fontSize: '0.85rem' }}>
                    Recommendations to Review ({recs.length})
                  </Typography>

                  {recs.map((rec) => (
                    <Paper
                      key={rec.id}
                      variant="outlined"
                      sx={{ p: 2, mb: 1, borderRadius: 2, display: 'flex', alignItems: 'flex-start', gap: 1.5 }}
                    >
                      <Checkbox
                        checked={!!selectedRecs[entry.analysis_id]?.[rec.id]}
                        onChange={() => toggleRec(entry.analysis_id, rec.id)}
                        size="small"
                        sx={{ mt: -0.5 }}
                      />
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2" fontWeight={600} sx={{ fontSize: '0.85rem' }}>{rec.resource_name}</Typography>
                          <Typography variant="body2" fontWeight={700} color="success.main" sx={{ fontSize: '0.85rem' }}>
                            <TrendingDown sx={{ fontSize: 14, mr: 0.3, verticalAlign: 'middle' }} />
                            {fmt(rec.estimated_savings)}/mo
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>{rec.description}</Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                          <Chip label={rec.action?.replace(/_/g, ' ')} size="small" variant="outlined" sx={{ height: 20, fontSize: 10 }} />
                          <Chip
                            label={`${Math.round((rec.confidence || 0) * 100)}%`}
                            size="small"
                            color={rec.confidence >= 0.85 ? 'success' : rec.confidence >= 0.6 ? 'warning' : 'error'}
                            sx={{ height: 20, fontSize: 10 }}
                          />
                          <Chip label={rec.risk_level} size="small" variant="outlined"
                            color={rec.risk_level === 'high' ? 'error' : rec.risk_level === 'medium' ? 'warning' : 'success'}
                            sx={{ height: 20, fontSize: 10 }} />
                          <Chip label={`${rec.current_config} → ${rec.recommended_config}`} size="small" variant="outlined" sx={{ height: 20, fontSize: 10 }} />
                        </Box>
                      </Box>
                    </Paper>
                  ))}

                  {/* Notes */}
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    placeholder="Add review notes (optional)..."
                    value={notes[entry.analysis_id] || ''}
                    onChange={(e) => setNotes((prev) => ({ ...prev, [entry.analysis_id]: e.target.value }))}
                    sx={{ mt: 2, mb: 2 }}
                    size="small"
                  />

                  {/* Action Buttons */}
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={isProcessing ? <CircularProgress size={16} color="inherit" /> : <CheckCircle />}
                      onClick={() => handleReview(entry.analysis_id, 'approve')}
                      disabled={isProcessing}
                      sx={{ flex: 1 }}
                    >
                      Approve All
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<Cancel />}
                      onClick={() => handleReview(entry.analysis_id, 'reject')}
                      disabled={isProcessing}
                      sx={{ flex: 1 }}
                    >
                      Reject All
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            );
          })}
        </Box>
      )}

      <Snackbar open={snack.open} autoHideDuration={4000} onClose={() => setSnack({ ...snack, open: false })}>
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>{snack.msg}</Alert>
      </Snackbar>
    </Box>
  );
}
