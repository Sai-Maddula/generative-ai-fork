import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Grid, Card, CardContent, CardActionArea, Typography, Button,
  LinearProgress, Chip, CircularProgress, Alert, Snackbar, FormControl,
  InputLabel, Select, MenuItem
} from '@mui/material';
import { AttachMoney, Savings, HealthAndSafety, Warning, PlayArrow } from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getSubscriptions, getSummary, getCostTrends, getProvisioningEntities, getOrganizations } from '../../services/api';
import AgentWorkflowTracker from '../AgentWorkflowTracker/AgentWorkflowTracker';
import ProviderBadge from '../ProviderBadge/ProviderBadge';
import FreshnessBadge from '../FreshnessBadge/FreshnessBadge';
import { useAppStore } from '../../store/store';
import { formatLastAnalyzed, isAnalysisStale } from '../../utils/freshnessUtils';

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
const healthColor = (h) => (h >= 75 ? '#2e7d32' : h >= 50 ? '#ed6c02' : '#d32f2f');

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <Card
      sx={{
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
        }
      }}
    >
      <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 1.2 }}>
        <Box
          sx={{
            bgcolor: color,
            borderRadius: 2,
            p: 1,
            display: 'flex',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '.MuiCard-root:hover &': {
              transform: 'scale(1.1) rotate(5deg)',
            }
          }}
        >
          <Icon sx={{ color: '#fff', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>{title}</Typography>
          <Typography variant="body1" fontWeight={600} sx={{ fontSize: '1.1rem' }}>{value}</Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
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
  const [subs, setSubs] = useState([]);
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snack, setSnack] = useState({ open: false, msg: '', severity: 'success' });
  const [provisioningEntities, setProvisioningEntities] = useState([]);
  const [organizations, setOrganizations] = useState([]);

  // Workflow tracker state
  const [trackerOpen, setTrackerOpen] = useState(false);
  const [trackerSubId, setTrackerSubId] = useState(null);
  const [trackerSubName, setTrackerSubName] = useState('');

  useEffect(() => {
    loadHierarchy();
  }, []);

  useEffect(() => {
    loadData();
  }, [selectedProvider, selectedProvisioningEntity, selectedOrganization]);

  // Update page title based on selected provider
  useEffect(() => {
    document.title = getPageTitle();
  }, [selectedProvider]);

  // Load organizations when provisioning entity changes
  useEffect(() => {
    loadOrganizations();
  }, [selectedProvisioningEntity]);

  const loadHierarchy = async () => {
    try {
      const entitiesRes = await getProvisioningEntities();
      setProvisioningEntities(entitiesRes.data);
      if (selectedProvisioningEntity) {
        loadOrganizations();
      }
    } catch (err) {
      console.error('Error loading hierarchy:', err);
    }
  };

  const loadOrganizations = async () => {
    try {
      const orgsRes = await getOrganizations(selectedProvisioningEntity);
      setOrganizations(orgsRes.data);
    } catch (err) {
      console.error('Error loading organizations:', err);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [subsRes, summaryRes, trendsRes] = await Promise.all([
        getSubscriptions(selectedProvisioningEntity, selectedOrganization),
        getSummary(selectedProvider, selectedProvisioningEntity, selectedOrganization),
        getCostTrends(selectedProvider, selectedProvisioningEntity, selectedOrganization),
      ]);
      setSubs(subsRes.data);
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = (subId, subName, e) => {
    e.stopPropagation();
    setTrackerSubId(subId);
    setTrackerSubName(subName);
    setTrackerOpen(true);
  };

  const handleTrackerComplete = (result) => {
    setSnack({
      open: true,
      msg: `Analysis complete: ${result.anomaly_count} anomalies, ${result.recommendation_count} recommendations, ${fmt(result.total_potential_savings)} savings`,
      severity: result.hitl_required ? 'warning' : 'success',
    });
    // Don't reload data here - let handleTrackerClose do it when drawer actually closes
  };

  const handleTrackerClose = () => {
    setTrackerOpen(false);
    setTrackerSubId(null);
    setTrackerSubName('');
    // Small delay to ensure drawer is fully closed before reloading
    setTimeout(() => loadData(), 100);
  };

  // Filter subscriptions by provider and selected subscription
  const filteredSubs = subs.filter(sub => {
    const subProvider = (sub.provider || 'azure').toLowerCase();
    if (subProvider !== selectedProvider) return false;
    if (selectedSubscription && sub.id !== selectedSubscription) return false;
    return true;
  });

  // Get provider-specific title
  const getPageTitle = () => {
    if (selectedProvider === 'azure') return 'Azure Cost Optimizer';
    if (selectedProvider === 'aws') return 'AWS Cost Explorer';
    return 'Azure Cost Optimizer';
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;

  const handleProvisioningEntityChange = (event) => {
    const value = event.target.value === '' ? null : event.target.value;
    setSelectedProvisioningEntity(value);
    setSelectedOrganization(null);
    setSelectedSubscription(null);
  };

  const handleOrganizationChange = (event) => {
    const value = event.target.value === '' ? null : event.target.value;
    setSelectedOrganization(value);
    setSelectedSubscription(null);
  };

  const handleSubscriptionChange = (event) => {
    const value = event.target.value === '' ? null : event.target.value;
    setSelectedSubscription(value);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.15rem' }}>{getPageTitle()}</Typography>
      </Box>

      {/* Hierarchy Filters */}
      <Card sx={{ mb: 1.5, p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600 }}>
          Filter by Hierarchy
        </Typography>
        <Grid container spacing={2}>
          {selectedProvider === 'azure' && (
            <>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Provisioning Entity</InputLabel>
                  <Select
                    value={selectedProvisioningEntity || ''}
                    onChange={handleProvisioningEntityChange}
                    label="Provisioning Entity"
                  >
                    <MenuItem value="">
                      <em>All Provisioning Entities</em>
                    </MenuItem>
                    {provisioningEntities.map((entity) => (
                      <MenuItem key={entity.id} value={entity.id}>
                        {entity.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth size="small" disabled={!selectedProvisioningEntity}>
                  <InputLabel>Organization</InputLabel>
                  <Select
                    value={selectedOrganization || ''}
                    onChange={handleOrganizationChange}
                    label="Organization"
                  >
                    <MenuItem value="">
                      <em>All Organizations</em>
                    </MenuItem>
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
          <Grid item xs={12} sm={6} md={selectedProvider === 'azure' ? 4 : 12}>
            <FormControl fullWidth size="small">
              <InputLabel>Subscription</InputLabel>
              <Select
                value={selectedSubscription || ''}
                onChange={handleSubscriptionChange}
                label="Subscription"
              >
                <MenuItem value="">
                  <em>All Subscriptions</em>
                </MenuItem>
                {subs.filter(s => {
                  const subProvider = (s.provider || 'azure').toLowerCase();
                  return subProvider === selectedProvider;
                }).map((sub) => (
                  <MenuItem key={sub.id} value={sub.id}>
                    {sub.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Card>

      {/* Summary Cards */}
      <Grid container spacing={1.5} sx={{ mb: 1.5 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Monthly Spend" value={fmt(summary?.total_spend)} icon={AttachMoney} color="#0078d4" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Potential Savings" value={fmt(summary?.total_savings)} icon={Savings} color="#2e7d32" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Avg Health Score" value={`${Math.round(summary?.avg_health || 0)} / 100`} icon={HealthAndSafety} color="#ed6c02" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Anomalies" value={summary?.total_anomalies || 0} icon={Warning} color="#d32f2f" />
        </Grid>
      </Grid>

      {/* Cost Trend Chart */}
      <Card
        sx={{
          mb: 1.5,
          p: 1.2,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 16px rgba(0,0,0,0.12)',
          }
        }}
      >
        <Typography variant="h6" sx={{ mb: 1, fontSize: '0.95rem', fontWeight: 600 }}>Cost Trends (Last 30 Days)</Typography>
        {trends.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="costGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0078d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0078d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis
                tickFormatter={(v) => v >= 1000 ? `$${(v / 1000).toFixed(1)}k` : `$${v.toFixed(0)}`}
                domain={['auto', 'auto']}
              />
              <Tooltip formatter={(v) => [fmt(v), 'Daily Cost']} labelFormatter={(l) => `Date: ${l}`} />
              <Area type="monotone" dataKey="cost" stroke="#0078d4" fill="url(#costGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No cost trend data available. Run an analysis to generate cost history.
            </Typography>
          </Box>
        )}
      </Card>

      {/* Subscription Cards */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
        <Typography variant="h6" sx={{ fontSize: '0.95rem', fontWeight: 600 }}>
          {selectedProvider === 'azure' && 'Azure Subscriptions'}
          {selectedProvider === 'aws' && 'AWS Accounts'}
          <Chip
            label={`${filteredSubs.length}`}
            size="small"
            sx={{ ml: 2 }}
          />
        </Typography>
      </Box>

      {filteredSubs.length === 0 ? (
        <Alert severity="info" sx={{ mb: 1.5 }}>
          No {selectedProvider.toUpperCase()} subscriptions found.
        </Alert>
      ) : (
        <Grid container spacing={1.5}>
          {filteredSubs.map((sub) => (
          <Grid item xs={12} sm={6} md={4} key={sub.id}>
            <Card
              sx={{
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                border: '2px solid transparent',
                '&:hover': {
                  transform: 'translateY(-8px) scale(1.02)',
                  boxShadow: '0 16px 32px rgba(0,0,0,0.2)',
                  borderColor: healthColor(sub.health_score),
                }
              }}
            >
              <CardActionArea
                onClick={() => navigate(`/subscriptions/${sub.id}`)}
                sx={{
                  transition: 'background-color 0.3s ease',
                  '&:hover': {
                    bgcolor: 'rgba(0, 120, 212, 0.04)',
                  }
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.75, gap: 1 }}>
                    <Typography variant="body1" noWrap sx={{ maxWidth: 180, flex: 1, fontWeight: 600, fontSize: '0.9rem' }}>{sub.name}</Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, alignItems: 'flex-end' }}>
                      <ProviderBadge provider={sub.provider || 'azure'} size="small" />
                      <Chip label={sub.environment} size="small" color="primary" variant="outlined" />
                    </Box>
                  </Box>
                  <Box sx={{ mb: 1.5 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>Health Score</Typography>
                      <Typography variant="body2" fontWeight={600} sx={{ color: healthColor(sub.health_score), fontSize: '0.8rem' }}>
                        {sub.health_score}/100
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={sub.health_score}
                      sx={{
                        height: 6, borderRadius: 3,
                        bgcolor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': { bgcolor: healthColor(sub.health_score), borderRadius: 3 },
                      }}
                    />
                  </Box>
                  <Box sx={{ mb: 1.2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem', flex: 1 }}>
                      {formatLastAnalyzed(sub.last_analyzed_at)}
                    </Typography>
                    <FreshnessBadge lastAnalyzedAt={sub.last_analyzed_at} size="small" />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>Spend: <strong>{fmt(sub.current_spend)}</strong>/mo</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>{sub.resource_count} resources</Typography>
                  </Box>
                </CardContent>
              </CardActionArea>
              <Box sx={{ px: 1.5, pb: 1.5 }}>
                <Button
                  fullWidth variant="contained" size="small"
                  startIcon={trackerOpen && trackerSubId === sub.id ? <CircularProgress size={16} color="inherit" /> : <PlayArrow />}
                  onClick={(e) => handleAnalyze(sub.id, sub.name, e)}
                  disabled={trackerOpen && trackerSubId === sub.id}
                  sx={{
                    background: selectedProvider === 'azure'
                      ? 'linear-gradient(135deg, #0078d4 0%, #1e88e5 100%)'
                      : 'linear-gradient(135deg, #FF9900 0%, #FF6F00 100%)',
                    color: '#ffffff',
                    fontWeight: 600,
                    textTransform: 'none',
                    py: 0.75,
                    position: 'relative',
                    overflow: 'hidden',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    boxShadow: selectedProvider === 'azure'
                      ? '0 4px 12px rgba(0, 120, 212, 0.3)'
                      : '0 4px 12px rgba(255, 153, 0, 0.3)',
                    // Pulse animation for stale data
                    ...(isAnalysisStale(sub.last_analyzed_at) && {
                      animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                      '@keyframes pulse': {
                        '0%, 100%': {
                          opacity: 1,
                        },
                        '50%': {
                          opacity: 0.85,
                        },
                      },
                    }),
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: '-100%',
                      width: '100%',
                      height: '100%',
                      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                      transition: 'left 0.5s',
                    },
                    '&:hover:not(:disabled)': {
                      transform: 'translateY(-2px) scale(1.02)',
                      boxShadow: selectedProvider === 'azure'
                        ? '0 8px 20px rgba(0, 120, 212, 0.5)'
                        : '0 8px 20px rgba(255, 153, 0, 0.5)',
                      '&::before': {
                        left: '100%',
                      },
                    },
                    '&:active:not(:disabled)': {
                      transform: 'translateY(0) scale(0.98)',
                    },
                    '&:disabled': {
                      background: 'linear-gradient(135deg, #bdbdbd 0%, #9e9e9e 100%)',
                      color: '#ffffff',
                      opacity: 0.7,
                    }
                  }}
                >
                  {trackerOpen && trackerSubId === sub.id ? 'Analyzing...' : 'Run Analysis'}
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
        </Grid>
      )}

      {/* Agent Workflow Tracker Drawer */}
      <AgentWorkflowTracker
        open={trackerOpen}
        onClose={handleTrackerClose}
        subscriptionId={trackerSubId}
        subscriptionName={trackerSubName}
        onComplete={handleTrackerComplete}
        onViewResults={(subId) => {
          setTrackerOpen(false);
          navigate(`/subscriptions/${subId}`);
        }}
      />

      <Snackbar open={snack.open} autoHideDuration={6000} onClose={() => setSnack({ ...snack, open: false })}>
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>{snack.msg}</Alert>
      </Snackbar>
    </Box>
  );
}
