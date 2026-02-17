import { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Select, MenuItem,
  FormControl, InputLabel, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress
} from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from 'recharts';
import { getSubscriptions, getAllForecasts, getCostTrends, getProvisioningEntities, getOrganizations } from '../../services/api';
import { useAppStore } from '../../store/store';

const fmt = (v) => `$${(v || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

const trendConfig = {
  increasing: { icon: TrendingUp, color: '#d32f2f', label: 'Increasing' },
  decreasing: { icon: TrendingDown, color: '#2e7d32', label: 'Decreasing' },
  stable: { icon: TrendingFlat, color: '#ed6c02', label: 'Stable' },
};

function generateProjectionData(history, forecastDays = 30) {
  if (!history || history.length === 0) return [];

  const recent = history.slice(-30);
  const avgCost = recent.reduce((s, h) => s + h.cost, 0) / recent.length;
  const dailyGrowth = avgCost * 0.001; // ~3% monthly growth

  const data = recent.map((h) => ({
    date: h.date,
    actual: h.cost,
    projected: null,
    optimized: null,
  }));

  const lastDate = new Date(recent[recent.length - 1]?.date || new Date());
  for (let i = 1; i <= forecastDays; i++) {
    const d = new Date(lastDate);
    d.setDate(d.getDate() + i);
    const dateStr = d.toISOString().slice(0, 10);
    const projected = avgCost + dailyGrowth * i + (Math.random() - 0.5) * avgCost * 0.05;
    data.push({
      date: dateStr,
      actual: null,
      projected: Math.round(projected),
      optimized: Math.round(projected * 0.82),
    });
  }
  return data;
}

export default function Forecasting() {
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
  const [forecasts, setForecasts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [provisioningEntities, setProvisioningEntities] = useState([]);
  const [organizations, setOrganizations] = useState([]);

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
      const [subsRes, forecastsRes, trendsRes] = await Promise.all([
        getSubscriptions(selectedProvisioningEntity, selectedOrganization, selectedProvider),
        getAllForecasts(selectedProvider, selectedProvisioningEntity, selectedOrganization),
        getCostTrends(selectedProvider, selectedProvisioningEntity, selectedOrganization),
      ]);
      setSubs(subsRes.data);
      setForecasts(forecastsRes.data);
      setTrends(trendsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectedForecast = !selectedSubscription
    ? {
        forecast_30d: forecasts.reduce((s, f) => s + (f.forecast_30d || 0), 0),
        forecast_90d: forecasts.reduce((s, f) => s + (f.forecast_90d || 0), 0),
        forecast_with_optimization: forecasts.reduce((s, f) => s + (f.forecast_with_optimization || 0), 0),
        savings_if_adopted: forecasts.reduce((s, f) => s + (f.savings_if_adopted || 0), 0),
        trend: 'increasing',
      }
    : forecasts.find((f) => f.subscription_id === selectedSubscription) || {};

  const chartData = generateProjectionData(trends);
  const todayStr = new Date().toISOString().slice(0, 10);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.15rem', mb: 1 }}>Cost Forecasting</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '0.8rem' }}>
        AI-powered spend projections with and without optimization adoption
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

      {/* Forecast Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>30-Day Forecast</Typography>
              <Typography variant="body1" fontWeight={600} sx={{ fontSize: '1.1rem' }}>{fmt(selectedForecast.forecast_30d)}</Typography>
              {(() => {
                const t = trendConfig[selectedForecast.trend] || trendConfig.stable;
                const Icon = t.icon;
                return <Chip icon={<Icon />} label={t.label} size="small" sx={{ mt: 1, color: t.color, borderColor: t.color }} variant="outlined" />;
              })()}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>90-Day Forecast</Typography>
              <Typography variant="body1" fontWeight={600} sx={{ fontSize: '1.1rem' }}>{fmt(selectedForecast.forecast_90d)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>Savings if Optimized</Typography>
              <Typography variant="body1" fontWeight={600} color="success.main" sx={{ fontSize: '1.1rem' }}>{fmt(selectedForecast.savings_if_adopted)}</Typography>
              {selectedForecast.forecast_30d > 0 && (
                <Typography variant="body2" color="success.main" sx={{ fontSize: '0.8rem' }}>
                  {Math.round((selectedForecast.savings_if_adopted / selectedForecast.forecast_30d) * 100)}% reduction
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Projection Chart */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 600 }}>Cost Projection</Typography>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
            <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
            <Tooltip formatter={(v) => [v ? fmt(v) : 'N/A']} />
            <Legend />
            <ReferenceLine x={todayStr} stroke="#666" strokeDasharray="5 5" label="Today" />
            <Line type="monotone" dataKey="actual" stroke="#0078d4" strokeWidth={2} name="Actual" dot={false} connectNulls={false} />
            <Line type="monotone" dataKey="projected" stroke="#d32f2f" strokeWidth={2} strokeDasharray="5 5" name="Projected (No Change)" dot={false} connectNulls={false} />
            <Line type="monotone" dataKey="optimized" stroke="#2e7d32" strokeWidth={2} strokeDasharray="5 5" name="With Optimization" dot={false} connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Forecast Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 600 }}>Subscription Forecasts</Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                  <TableCell><strong>Subscription</strong></TableCell>
                  <TableCell align="right"><strong>30-Day</strong></TableCell>
                  <TableCell align="right"><strong>90-Day</strong></TableCell>
                  <TableCell align="right"><strong>Optimized</strong></TableCell>
                  <TableCell align="right"><strong>Savings</strong></TableCell>
                  <TableCell><strong>Trend</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {forecasts.map((f) => {
                  const t = trendConfig[f.trend] || trendConfig.stable;
                  const Icon = t.icon;
                  return (
                    <TableRow key={f.subscription_id} hover>
                      <TableCell>{f.subscription_name || f.subscription_id}</TableCell>
                      <TableCell align="right">{fmt(f.forecast_30d)}</TableCell>
                      <TableCell align="right">{fmt(f.forecast_90d)}</TableCell>
                      <TableCell align="right">{fmt(f.forecast_with_optimization)}</TableCell>
                      <TableCell align="right">
                        <Typography color="success.main" fontWeight={600}>{fmt(f.savings_if_adopted)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip icon={<Icon />} label={t.label} size="small" sx={{ color: t.color, borderColor: t.color }} variant="outlined" />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}