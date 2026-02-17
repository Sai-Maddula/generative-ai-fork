import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Grid, Card, CardContent, Typography, Button, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Chip,
  LinearProgress, CircularProgress, Alert, Snackbar, Fab
} from '@mui/material';
import { ArrowBack, PlayArrow } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getSubscription, getRecommendations } from '../../services/api';
import AgentWorkflowTracker from '../AgentWorkflowTracker/AgentWorkflowTracker';
import HealthScoreBreakdown from '../HealthScoreBreakdown/HealthScoreBreakdown';

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
const healthColor = (h) => (h >= 75 ? '#2e7d32' : h >= 50 ? '#ed6c02' : '#d32f2f');
const utilColor = (v) => (v >= 60 ? '#2e7d32' : v >= 30 ? '#ed6c02' : '#d32f2f');

export default function SubscriptionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [sub, setSub] = useState(null);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snack, setSnack] = useState({ open: false, msg: '', severity: 'success' });
  const [trackerOpen, setTrackerOpen] = useState(false);

  useEffect(() => { loadData(); }, [id]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [subRes, recsRes] = await Promise.all([
        getSubscription(id),
        getRecommendations({ subscription_id: id }),
      ]);
      setSub(subRes.data);
      setRecs(recsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrackerComplete = (result) => {
    setSnack({
      open: true,
      msg: `Analysis complete: ${result.anomaly_count} anomalies, ${result.recommendation_count} recommendations`,
      severity: 'success',
    });
    // Don't reload data here - let onClose handle it
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;
  if (!sub) return <Alert severity="error">Subscription not found</Alert>;

  const resources = sub.resources || [];
  const costHistory = (sub.cost_history || []).map((h) => ({
    ...h,
    daily_cost: typeof h.daily_cost === 'number' ? h.daily_cost : parseFloat(h.daily_cost) || 0,
  }));

  return (
    <Box>
      <Button startIcon={<ArrowBack />} onClick={() => navigate('/')} sx={{ mb: 2 }}>
        Back to Dashboard
      </Button>

      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600, fontSize: '1.2rem' }}>{sub.name}</Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip label={sub.environment} color="primary" size="small" />
                <Chip label={sub.region} variant="outlined" size="small" />
                <Chip label={`Owner: ${sub.owner}`} variant="outlined" size="small" />
              </Box>
            </Box>
            <Box sx={{ minWidth: 280 }}>
              <HealthScoreBreakdown
                healthScore={sub.health_score}
                healthComponents={sub.health_components || (() => {
                  const h = sub.health_score || 65;
                  return {
                    cost_efficiency: Math.min(100, h + 8),
                    resource_utilization: Math.min(100, h - 5),
                    optimization_adoption: Math.max(0, h - 15),
                    anomaly_frequency: Math.min(100, h + 12),
                  };
                })()}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { label: 'Resources', value: sub.resource_count || resources.length },
          { label: 'Monthly Spend', value: fmt(sub.current_spend) },
          { label: 'Budget', value: fmt(sub.monthly_budget) },
          { label: 'Recommendations', value: recs.length },
        ].map((s) => (
          <Grid item xs={6} sm={3} key={s.label}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="body1" fontWeight={600} sx={{ fontSize: '1.1rem' }}>{s.value}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>{s.label}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Cost History Chart */}
      {costHistory.length > 0 && (
        <Card sx={{ mb: 3, p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 600 }}>Cost History (Last 30 Days)</Typography>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={costHistory.slice(-30)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => d.slice(8)} />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(v) => [fmt(v), 'Daily Cost']} labelFormatter={(l) => `Date: ${l}`} />
              <Bar dataKey="daily_cost" fill="#0078d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Resources Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 600 }}>Resources</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                  <TableCell><strong>Name</strong></TableCell>
                  <TableCell><strong>Type</strong></TableCell>
                  <TableCell><strong>SKU</strong></TableCell>
                  <TableCell><strong>Region</strong></TableCell>
                  <TableCell align="right"><strong>Cost/mo</strong></TableCell>
                  <TableCell><strong>CPU %</strong></TableCell>
                  <TableCell><strong>Memory %</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {resources.sort((a, b) => (b.monthly_cost || 0) - (a.monthly_cost || 0)).map((r) => (
                  <TableRow key={r.id} hover>
                    <TableCell><Typography variant="body2" fontWeight={600} sx={{ fontSize: '0.85rem' }}>{r.name}</Typography></TableCell>
                    <TableCell><Typography variant="body2" sx={{ fontSize: '0.85rem' }}>{r.type}</Typography></TableCell>
                    <TableCell><Chip label={r.sku} size="small" variant="outlined" /></TableCell>
                    <TableCell><Typography variant="caption" sx={{ fontSize: '0.75rem' }}>{r.region}</Typography></TableCell>
                    <TableCell align="right"><Typography fontWeight={600} sx={{ fontSize: '0.85rem' }}>{fmt(r.monthly_cost)}</Typography></TableCell>
                    <TableCell sx={{ minWidth: 100 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress variant="determinate" value={r.cpu_usage_pct || 0}
                          sx={{ flex: 1, height: 6, borderRadius: 3, '& .MuiLinearProgress-bar': { bgcolor: utilColor(r.cpu_usage_pct) } }} />
                        <Typography variant="caption" sx={{ minWidth: 30 }}>{Math.round(r.cpu_usage_pct || 0)}%</Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ minWidth: 100 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress variant="determinate" value={r.memory_usage_pct || 0}
                          sx={{ flex: 1, height: 6, borderRadius: 3, '& .MuiLinearProgress-bar': { bgcolor: utilColor(r.memory_usage_pct) } }} />
                        <Typography variant="caption" sx={{ minWidth: 30 }}>{Math.round(r.memory_usage_pct || 0)}%</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={r.is_active ? 'Active' : 'Inactive'} size="small" color={r.is_active ? 'success' : 'default'} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 600 }}>Recommendations</Typography>
          {recs.length === 0 ? (
            <Alert severity="info">No recommendations yet. Click "Run Analysis" to generate optimization suggestions.</Alert>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                    <TableCell><strong>Action</strong></TableCell>
                    <TableCell><strong>Resource</strong></TableCell>
                    <TableCell align="right"><strong>Savings</strong></TableCell>
                    <TableCell><strong>Confidence</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recs.map((r) => (
                    <TableRow key={r.id} hover>
                      <TableCell>{r.description}</TableCell>
                      <TableCell>{r.resource_name}</TableCell>
                      <TableCell align="right"><Typography color="success.main" fontWeight={600}>{fmt(r.estimated_savings)}</Typography></TableCell>
                      <TableCell>
                        <Chip label={`${Math.round(r.confidence * 100)}%`} size="small"
                          color={r.confidence >= 0.85 ? 'success' : r.confidence >= 0.6 ? 'warning' : 'error'} />
                      </TableCell>
                      <TableCell>
                        <Chip label={r.status} size="small"
                          color={r.status === 'approved' ? 'success' : r.status === 'rejected' ? 'error' : 'warning'} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Floating Analyze Button - offset right to avoid chat FAB */}
      <Fab variant="extended" color="primary" onClick={() => setTrackerOpen(true)} disabled={trackerOpen}
        sx={{ position: 'fixed', bottom: 24, right: 90 }}>
        {trackerOpen ? <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} /> : <PlayArrow sx={{ mr: 1 }} />}
        {trackerOpen ? 'Analyzing...' : 'Run Analysis'}
      </Fab>

      <AgentWorkflowTracker
        open={trackerOpen}
        onClose={() => {
          setTrackerOpen(false);
          setTimeout(() => loadData(), 100);
        }}
        subscriptionId={id}
        subscriptionName={sub?.name || ''}
        onComplete={handleTrackerComplete}
      />

      <Snackbar open={snack.open} autoHideDuration={5000} onClose={() => setSnack({ ...snack, open: false })}>
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>{snack.msg}</Alert>
      </Snackbar>
    </Box>
  );
}
