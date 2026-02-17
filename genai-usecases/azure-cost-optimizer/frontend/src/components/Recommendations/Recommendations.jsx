import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, Button, Tabs, Tab,
  Alert, CircularProgress, Snackbar, Tooltip, Collapse, LinearProgress,
  Dialog, DialogTitle, DialogContent, DialogActions, Grid, Divider,
  FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import { Check, Close, TrendingDown, Psychology, Gavel, CheckCircle, Visibility } from '@mui/icons-material';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import { getRecommendations, getHITLQueue, approveRecommendation, rejectRecommendation, getProvisioningEntities, getOrganizations, getSubscriptions } from '../../services/api';
import AgentReasoningPanel from '../AgentReasoningPanel/AgentReasoningPanel';
import ProviderBadge from '../ProviderBadge/ProviderBadge';
import { useAppStore } from '../../store/store';

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
const pct = (v) => `${Math.round((v || 0) * 100)}%`;

const riskColors = { low: 'success', medium: 'warning', high: 'error' };
const statusColors = { pending: 'warning', approved: 'success', rejected: 'error', implemented: 'info' };

// ========= NEW: Cost Impact Visualization Component =========
const CostImpactBar = ({ recommendation }) => {
  const currentCost = recommendation.estimated_savings / 0.3; // Approximate current cost
  const newCost = currentCost - recommendation.estimated_savings;
  const savingsPercent = ((recommendation.estimated_savings / currentCost) * 100).toFixed(0);
  const annualSavings = recommendation.estimated_savings * 12;

  return (
    <Box sx={{ my: 1 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={6}>
          <Typography variant="caption" color="text.secondary">Current Cost</Typography>
          <LinearProgress
            variant="determinate"
            value={100}
            sx={{ height: 24, borderRadius: 1, mb: 0.5, bgcolor: 'grey.200', '& .MuiLinearProgress-bar': { bgcolor: 'error.light' } }}
          />
          <Typography variant="body2" fontWeight={600}>{fmt(currentCost)}/month</Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="caption" color="text.secondary">After Optimization</Typography>
          <LinearProgress
            variant="determinate"
            value={(newCost / currentCost) * 100}
            sx={{ height: 24, borderRadius: 1, mb: 0.5, bgcolor: 'grey.200', '& .MuiLinearProgress-bar': { bgcolor: 'success.main' } }}
          />
          <Typography variant="body2" fontWeight={600}>{fmt(newCost)}/month</Typography>
        </Grid>
      </Grid>
      <Box sx={{ mt: 2, p: 2, bgcolor: 'success.50', borderRadius: 2, border: '1px solid', borderColor: 'success.light' }}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Monthly Savings</Typography>
            <Typography variant="h6" color="success.main" fontWeight={700}>
              <CountUp end={recommendation.estimated_savings} duration={1.5} prefix="$" decimals={0} />
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Annual Impact</Typography>
            <Typography variant="h6" color="success.main" fontWeight={700}>
              <CountUp end={annualSavings} duration={1.5} prefix="$" decimals={0} />
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Chip
              label={`${savingsPercent}% Cost Reduction`}
              color="success"
              size="small"
              sx={{ fontWeight: 600 }}
            />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

// ========= NEW: Live Preview Modal Component =========
const LivePreviewModal = ({ open, onClose, recommendation, onConfirm }) => {
  if (!recommendation) return null;

  const currentCost = recommendation.estimated_savings / 0.3;
  const newCost = currentCost - recommendation.estimated_savings;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Visibility color="primary" />
          <Typography variant="h6">Preview Changes</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Alert severity="info" sx={{ mb: 3 }}>
          Review the impact of this recommendation before applying
        </Alert>

        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          {recommendation.description}
        </Typography>

        <Grid container spacing={3} sx={{ mt: 1 }}>
          {/* BEFORE Column */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'error.50', border: '2px solid', borderColor: 'error.light' }}>
              <Typography variant="overline" color="error.main" fontWeight={700}>BEFORE (Current)</Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2"><strong>Configuration:</strong> {recommendation.current_config}</Typography>
                <Typography variant="body2"><strong>Cost:</strong> {fmt(currentCost)}/month</Typography>
                <Typography variant="body2"><strong>Status:</strong> {recommendation.resource_type}</Typography>
              </Box>
            </Paper>
          </Grid>

          {/* AFTER Column */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'success.50', border: '2px solid', borderColor: 'success.light' }}>
              <Typography variant="overline" color="success.main" fontWeight={700}>AFTER (Recommended)</Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2"><strong>Configuration:</strong> {recommendation.recommended_config}</Typography>
                <Typography variant="body2"><strong>Cost:</strong> {fmt(newCost)}/month</Typography>
                <Typography variant="body2"><strong>Savings:</strong> {fmt(recommendation.estimated_savings)}/month</Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Impact Summary */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.50', borderRadius: 2 }}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Impact Summary</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="body2">
              <strong>Risk Level:</strong>{' '}
              <Chip label={recommendation.risk_level} size="small" color={riskColors[recommendation.risk_level]} />
            </Typography>
            <Typography variant="body2">
              <strong>Confidence:</strong>{' '}
              <Chip label={pct(recommendation.confidence)} size="small" color={recommendation.confidence >= 0.85 ? 'success' : 'warning'} />
            </Typography>
            <Typography variant="body2">
              <strong>Annual Savings:</strong> {fmt(recommendation.estimated_savings * 12)}
            </Typography>
            {recommendation.risk_level === 'low' && (
              <Alert severity="success" sx={{ mt: 1 }}>
                ✓ Minimal performance impact expected. Easy to reverse if needed.
              </Alert>
            )}
            {recommendation.risk_level === 'high' && (
              <Alert severity="warning" sx={{ mt: 1 }}>
                ⚠️ High-risk action. Review carefully before proceeding.
              </Alert>
            )}
          </Box>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="outlined">Cancel</Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          color="success"
          startIcon={<CheckCircle />}
        >
          Confirm & Apply
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default function Recommendations() {
  const navigate = useNavigate();
  const {
    selectedProvider,
    selectedProvisioningEntity,
    selectedOrganization,
    selectedSubscription,
    setSelectedProvisioningEntity,
    setSelectedOrganization,
    setSelectedSubscription
  } = useAppStore();
  const [recs, setRecs] = useState([]);
  const [hitlQueue, setHitlQueue] = useState([]);
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [expandedRec, setExpandedRec] = useState(null);
  const [snack, setSnack] = useState({ open: false, msg: '', severity: 'success' });
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewRec, setPreviewRec] = useState(null);
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
      const [recsRes, hitlRes, subsRes] = await Promise.all([
        getRecommendations(selectedProvider, selectedProvisioningEntity, selectedOrganization),
        getHITLQueue(selectedProvider, selectedProvisioningEntity, selectedOrganization),
        getSubscriptions(selectedProvisioningEntity, selectedOrganization, selectedProvider)
      ]);
      setRecs(recsRes.data);
      setHitlQueue(hitlRes.data);
      setSubs(subsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    setActionLoading(id);
    try {
      await approveRecommendation(id);
      setSnack({ open: true, msg: 'Recommendation approved', severity: 'success' });
      loadData();
    } catch (err) {
      setSnack({ open: true, msg: 'Failed to approve', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id) => {
    setActionLoading(id);
    try {
      await rejectRecommendation(id);
      setSnack({ open: true, msg: 'Recommendation rejected', severity: 'info' });
      loadData();
    } catch (err) {
      setSnack({ open: true, msg: 'Failed to reject', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  // NEW: Open preview modal
  const handlePreviewApprove = (rec) => {
    setPreviewRec(rec);
    setPreviewOpen(true);
  };

  // NEW: Confirm approval from preview modal
  const handleConfirmApproval = async () => {
    if (previewRec) {
      setPreviewOpen(false);
      await handleApprove(previewRec.id);
      setPreviewRec(null);
    }
  };

  // NEW: One-click approve all low-risk recommendations
  const handleApproveAllLowRisk = async () => {
    const lowRiskRecs = recs.filter(
      r => r.status === 'pending' && r.risk_level === 'low' && r.confidence >= 0.70
    );

    if (lowRiskRecs.length === 0) {
      setSnack({ open: true, msg: 'No low-risk recommendations to approve', severity: 'info' });
      return;
    }

    setActionLoading('bulk');
    try {
      await Promise.all(lowRiskRecs.map(r => approveRecommendation(r.id)));
      setSnack({
        open: true,
        msg: `✓ Approved ${lowRiskRecs.length} low-risk recommendation(s)`,
        severity: 'success'
      });
      loadData();
    } catch (err) {
      setSnack({ open: true, msg: 'Failed to approve some recommendations', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  // Data is already filtered by backend based on provider/hierarchy
  const tabFilters = ['all', 'pending', 'approved', 'rejected'];
  const filtered = tab === 0 ? recs : recs.filter((r) => r.status === tabFilters[tab]);
  const totalSavings = recs.reduce((s, r) => s + (r.estimated_savings || 0), 0);
  const pendingCount = recs.filter((r) => r.status === 'pending').length;

  // Build a mock agent decision for any recommendation to show reasoning
  const buildReasoningDecision = (rec) => ({
    agent_name: 'Optimization Recommendation Agent',
    decision: `${rec.action?.replace(/_/g, ' ')} for ${rec.resource_name}`,
    confidence: rec.confidence,
    reasoning: `${rec.description}. Current configuration: ${rec.current_config}. Recommended: ${rec.recommended_config}. `
      + `Estimated savings: ${fmt(rec.estimated_savings)}/mo. Risk level: ${rec.risk_level}.`,
    flags: [rec.action?.replace(/_/g, ' '), rec.risk_level],
    requires_human_review: rec.confidence < 0.85 || rec.risk_level === 'high',
    processing_time: null,
  });

  // Get provider-specific title
  const getPageTitle = () => {
    if (selectedProvider === 'azure') return 'Azure Recommendations';
    if (selectedProvider === 'aws') return 'AWS Recommendations';
    return 'Azure Recommendations';
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', overflow: 'hidden' }}>
      {/* Header with Provider Filter */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.15rem' }}>{getPageTitle()}</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontSize: '0.8rem' }}>
            Review AI-generated optimization suggestions. Approve or reject to manage your cloud costs.
          </Typography>
        </Box>
      </Box>

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

      {/* HITL Alert - now links to Agent Review page */}
      {hitlQueue.length > 0 && (
        <Alert
          severity="warning"
          sx={{ mb: 3 }}
          action={
            <Button
              color="inherit"
              size="small"
              startIcon={<Gavel />}
              onClick={() => navigate('/agent-review')}
              sx={{ fontWeight: 600 }}
            >
              Review Now
            </Button>
          }
        >
          <strong>{hitlQueue.length} analysis result(s)</strong> require human review with full agent decision context.
          {hitlQueue.map((h) => (
            <Typography key={h.analysis_id} variant="body2" sx={{ mt: 0.5 }}>
              - {h.subscription_name}: {h.recommendations?.length || 0} recommendations (Priority: {h.priority})
            </Typography>
          ))}
        </Alert>
      )}

      {/* Summary Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ display: 'flex', gap: 4, alignItems: 'center', justifyContent: 'space-between', py: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', gap: 4 }}>
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>Total Recommendations</Typography>
              <Typography variant="body1" fontWeight={600} sx={{ fontSize: '1.1rem' }}>{recs.length}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>Potential Savings</Typography>
              <Typography variant="body1" fontWeight={600} color="success.main" sx={{ fontSize: '1.1rem' }}>
                <CountUp end={totalSavings} duration={2} prefix="$" decimals={0} />/mo
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>Pending Review</Typography>
              <Typography variant="body1" fontWeight={600} color="warning.main" sx={{ fontSize: '1.1rem' }}>{pendingCount}</Typography>
            </Box>
          </Box>
          {/* NEW: One-Click Approve Button */}
          {recs.filter(r => r.status === 'pending' && r.risk_level === 'low' && r.confidence >= 0.70).length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircle />}
                onClick={handleApproveAllLowRisk}
                disabled={actionLoading === 'bulk'}
                sx={{ whiteSpace: 'nowrap' }}
              >
                ✓ Approve All Low-Risk ({recs.filter(r => r.status === 'pending' && r.risk_level === 'low' && r.confidence >= 0.70).length})
              </Button>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label={`All (${recs.length})`} />
        <Tab label={`Pending (${pendingCount})`} />
        <Tab label={`Approved (${recs.filter((r) => r.status === 'approved').length})`} />
        <Tab label={`Rejected (${recs.filter((r) => r.status === 'rejected').length})`} />
      </Tabs>

      {/* Table */}
      {filtered.length === 0 ? (
        <Alert severity="info">No recommendations found. Run an analysis on a subscription to generate recommendations.</Alert>
      ) : (
        <TableContainer component={Paper} sx={{ maxWidth: '100%', overflowX: 'auto', width: '100%' }}>
          <Table sx={{ width: '100%', tableLayout: 'auto' }}>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                <TableCell sx={{ width: '7%' }}><strong>Provider</strong></TableCell>
                <TableCell sx={{ width: '15%' }}><strong>Resource</strong></TableCell>
                <TableCell sx={{ width: '25%' }}><strong>Action</strong></TableCell>
                <TableCell sx={{ width: '11%' }}><strong>Savings</strong></TableCell>
                <TableCell sx={{ width: '11%' }}><strong>Confidence</strong></TableCell>
                <TableCell sx={{ width: '8%' }}><strong>Risk</strong></TableCell>
                <TableCell sx={{ width: '10%' }}><strong>Status</strong></TableCell>
                <TableCell align="center" sx={{ width: '13%' }}><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((rec) => (
                <React.Fragment key={rec.id}>
                  <TableRow hover sx={{ cursor: 'pointer' }} onClick={() => setExpandedRec(expandedRec === rec.id ? null : rec.id)}>
                    <TableCell>
                      <ProviderBadge provider={rec.provider || rec.subscription_id?.startsWith('aws') ? 'aws' : 'azure'} size="small" showIcon={true} />
                    </TableCell>
                    <TableCell sx={{ maxWidth: 150 }}>
                      <Tooltip title={rec.resource_name} arrow>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          sx={{
                            fontSize: '0.85rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {rec.resource_name}
                        </Typography>
                      </Tooltip>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>{rec.resource_type}</Typography>
                    </TableCell>
                    <TableCell sx={{ maxWidth: 250 }}>
                      <Tooltip title={rec.description} arrow>
                        <Typography
                          variant="body2"
                          sx={{
                            fontSize: '0.85rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {rec.description}
                        </Typography>
                      </Tooltip>
                      <Tooltip title={`${rec.current_config} → ${rec.recommended_config}`} arrow>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{
                            fontSize: '0.7rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            display: 'block'
                          }}
                        >
                          {rec.current_config} → {rec.recommended_config}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={700} color="success.main">
                        <TrendingDown sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
                        {fmt(rec.estimated_savings)}/mo
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={pct(rec.confidence)}
                        size="small"
                        color={rec.confidence >= 0.85 ? 'success' : rec.confidence >= 0.6 ? 'warning' : 'error'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.risk_level} size="small" color={riskColors[rec.risk_level] || 'default'} variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.status} size="small" color={statusColors[rec.status] || 'default'} />
                    </TableCell>
                    <TableCell align="center" onClick={(e) => e.stopPropagation()}>
                      {rec.status === 'pending' ? (
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                          <Tooltip title="Preview & Approve">
                            <Button
                              size="small" variant="contained" color="success"
                              onClick={() => handlePreviewApprove(rec)}
                              disabled={actionLoading === rec.id}
                              sx={{ minWidth: 36, p: 0.5 }}
                            >
                              <Visibility fontSize="small" />
                            </Button>
                          </Tooltip>
                          <Tooltip title="Quick Approve">
                            <Button
                              size="small" variant="outlined" color="success"
                              onClick={() => handleApprove(rec.id)}
                              disabled={actionLoading === rec.id}
                              sx={{ minWidth: 36, p: 0.5 }}
                            >
                              <Check fontSize="small" />
                            </Button>
                          </Tooltip>
                          <Tooltip title="Reject">
                            <Button
                              size="small" variant="outlined" color="error"
                              onClick={() => handleReject(rec.id)}
                              disabled={actionLoading === rec.id}
                              sx={{ minWidth: 36, p: 0.5 }}
                            >
                              <Close fontSize="small" />
                            </Button>
                          </Tooltip>
                        </Box>
                      ) : (
                        <Tooltip title={rec.reviewed_by ? `by ${rec.reviewed_by}` : ''} arrow placement="top">
                          <div
                            style={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              width: '140px',
                              fontSize: '0.75rem',
                              color: 'rgba(0, 0, 0, 0.6)',
                              textAlign: 'center'
                            }}
                          >
                            {rec.reviewed_by ? `by ${rec.reviewed_by}` : '-'}
                          </div>
                        </Tooltip>
                      )}
                    </TableCell>
                  </TableRow>
                  {/* Expandable reasoning row */}
                  <TableRow>
                    <TableCell colSpan={8} sx={{ py: 0, border: expandedRec === rec.id ? undefined : 'none' }}>
                      <Collapse in={expandedRec === rec.id}>
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <Box sx={{ py: 1.5, px: 1 }}>
                            {/* NEW: Cost Impact Visualization */}
                            <CostImpactBar recommendation={rec} />
                            <Divider sx={{ my: 2 }} />
                            {/* Agent Reasoning Panel */}
                            <AgentReasoningPanel decision={buildReasoningDecision(rec)} />
                          </Box>
                        </motion.div>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* NEW: Live Preview Modal */}
      <LivePreviewModal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        recommendation={previewRec}
        onConfirm={handleConfirmApproval}
      />

      <Snackbar open={snack.open} autoHideDuration={4000} onClose={() => setSnack({ ...snack, open: false })}>
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>{snack.msg}</Alert>
      </Snackbar>
    </Box>
  );
}
