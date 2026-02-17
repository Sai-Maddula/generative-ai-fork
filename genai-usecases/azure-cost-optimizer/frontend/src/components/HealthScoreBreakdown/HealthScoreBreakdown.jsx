import { Box, Typography, LinearProgress, Paper } from '@mui/material';
import { MonetizationOn, Memory, TuneOutlined, NotificationsActive } from '@mui/icons-material';

const components = [
  { key: 'cost_efficiency', label: 'Cost Efficiency', weight: '30%', icon: <MonetizationOn sx={{ fontSize: 18 }} />, color: '#0078d4' },
  { key: 'resource_utilization', label: 'Resource Utilization', weight: '25%', icon: <Memory sx={{ fontSize: 18 }} />, color: '#7b1fa2' },
  { key: 'optimization_adoption', label: 'Optimization Adoption', weight: '25%', icon: <TuneOutlined sx={{ fontSize: 18 }} />, color: '#2e7d32' },
  { key: 'anomaly_frequency', label: 'Anomaly Frequency', weight: '20%', icon: <NotificationsActive sx={{ fontSize: 18 }} />, color: '#ed6c02' },
];

const scoreColor = (v) => (v >= 75 ? '#2e7d32' : v >= 50 ? '#ed6c02' : '#d32f2f');

export default function HealthScoreBreakdown({ healthComponents, healthScore }) {
  if (!healthComponents) return null;

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" fontWeight={600}>Health Score Breakdown</Typography>
        <Typography variant="h6" fontWeight={700} sx={{ color: scoreColor(healthScore) }}>
          {healthScore}/100
        </Typography>
      </Box>

      {components.map((comp) => {
        const value = healthComponents[comp.key] || 0;
        return (
          <Box key={comp.key} sx={{ mb: 1.5 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                <Box sx={{ color: comp.color }}>{comp.icon}</Box>
                <Typography variant="caption" fontWeight={500}>{comp.label}</Typography>
                <Typography variant="caption" color="text.secondary">({comp.weight})</Typography>
              </Box>
              <Typography variant="caption" fontWeight={700} sx={{ color: scoreColor(value) }}>
                {Math.round(value)}/100
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={value}
              sx={{
                height: 6, borderRadius: 3,
                bgcolor: '#e8e8e8',
                '& .MuiLinearProgress-bar': { bgcolor: comp.color, borderRadius: 3, transition: 'transform 0.8s ease' },
              }}
            />
          </Box>
        );
      })}
    </Paper>
  );
}
