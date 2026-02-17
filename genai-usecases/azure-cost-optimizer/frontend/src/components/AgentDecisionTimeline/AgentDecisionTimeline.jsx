import { Box, Typography, Chip, Paper } from '@mui/material';
import {
  BugReport, Lightbulb, Gavel, TrendingUp, EmojiEvents,
  CheckCircle, Warning, Info,
} from '@mui/icons-material';

const agentIcons = {
  'Anomaly Detection Agent': <BugReport fontSize="small" />,
  'Optimization Recommendation Agent': <Lightbulb fontSize="small" />,
  'HITL Checkpoint Agent': <Gavel fontSize="small" />,
  'Forecasting Agent': <TrendingUp fontSize="small" />,
  'Gamification Agent': <EmojiEvents fontSize="small" />,
};

const agentColors = {
  'Anomaly Detection Agent': '#d32f2f',
  'Optimization Recommendation Agent': '#0078d4',
  'HITL Checkpoint Agent': '#ed6c02',
  'Forecasting Agent': '#7b1fa2',
  'Gamification Agent': '#2e7d32',
};

export default function AgentDecisionTimeline({ decisions = [], compact = false }) {
  if (!decisions || decisions.length === 0) return null;

  return (
    <Box sx={{ position: 'relative', pl: 3 }}>
      {/* Vertical line */}
      <Box
        sx={{
          position: 'absolute',
          left: 11,
          top: 8,
          bottom: 8,
          width: 2,
          bgcolor: '#e0e0e0',
          borderRadius: 1,
        }}
      />

      {decisions.map((d, i) => {
        const color = agentColors[d.agent_name] || '#0078d4';
        const icon = agentIcons[d.agent_name] || <Info fontSize="small" />;

        return (
          <Box key={i} sx={{ position: 'relative', mb: compact ? 1.5 : 2.5 }}>
            {/* Dot on the timeline */}
            <Box
              sx={{
                position: 'absolute',
                left: -23,
                top: 4,
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                boxShadow: `0 0 0 3px ${color}22`,
              }}
            >
              {icon}
            </Box>

            {/* Content */}
            <Paper
              variant="outlined"
              sx={{
                p: compact ? 1.5 : 2,
                borderRadius: 2,
                borderLeft: `3px solid ${color}`,
                bgcolor: '#fafafa',
                '&:hover': { bgcolor: '#f5f5f5' },
                transition: 'background 0.2s',
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant={compact ? 'body2' : 'subtitle2'} fontWeight={600} sx={{ color }}>
                  {d.agent_name}
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {d.confidence != null && (
                    <Chip
                      label={`${Math.round(d.confidence * 100)}%`}
                      size="small"
                      color={d.confidence >= 0.85 ? 'success' : d.confidence >= 0.6 ? 'warning' : 'error'}
                      sx={{ height: 20, fontSize: 11 }}
                    />
                  )}
                  {d.processing_time && (
                    <Chip label={`${d.processing_time.toFixed(1)}s`} size="small" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                  )}
                </Box>
              </Box>

              <Typography variant="body2" fontWeight={500} sx={{ mb: 0.5 }}>
                {d.decision}
              </Typography>

              {!compact && d.reasoning && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  {d.reasoning}
                </Typography>
              )}

              {d.flags && d.flags.length > 0 && (
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                  {d.flags.map((flag, fi) => (
                    <Chip
                      key={fi}
                      icon={d.requires_human_review ? <Warning sx={{ fontSize: 14 }} /> : <CheckCircle sx={{ fontSize: 14 }} />}
                      label={flag.replace(/_/g, ' ')}
                      size="small"
                      variant="outlined"
                      color={d.requires_human_review ? 'warning' : 'default'}
                      sx={{ height: 22, fontSize: 11 }}
                    />
                  ))}
                </Box>
              )}
            </Paper>
          </Box>
        );
      })}
    </Box>
  );
}
