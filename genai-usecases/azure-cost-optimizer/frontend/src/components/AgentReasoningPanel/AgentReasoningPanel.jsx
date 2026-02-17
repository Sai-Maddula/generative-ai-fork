import { useState } from 'react';
import { Box, Typography, Chip, Paper, Button, Collapse, LinearProgress } from '@mui/material';
import { Psychology, Speed, Warning, CheckCircle } from '@mui/icons-material';

export default function AgentReasoningPanel({ decision, compact = false }) {
  const [expanded, setExpanded] = useState(false);

  if (!decision) return null;

  const confidenceColor = decision.confidence >= 0.85 ? '#2e7d32' : decision.confidence >= 0.6 ? '#ed6c02' : '#d32f2f';

  return (
    <Box>
      <Button
        size="small"
        startIcon={<Psychology sx={{ fontSize: 16 }} />}
        onClick={() => setExpanded(!expanded)}
        sx={{
          textTransform: 'none',
          fontSize: '0.75rem',
          color: '#0078d4',
          '&:hover': { bgcolor: 'rgba(0,120,212,0.06)' },
        }}
      >
        {expanded ? 'Hide reasoning' : 'Why?'}
      </Button>

      <Collapse in={expanded}>
        <Paper
          variant="outlined"
          sx={{
            p: 2, mt: 0.5,
            borderRadius: 2,
            borderLeft: `3px solid ${confidenceColor}`,
            bgcolor: '#f8f9fa',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2" fontWeight={600} color="primary">
              {decision.agent_name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {decision.confidence != null && (
                <Chip
                  label={`${Math.round(decision.confidence * 100)}% confidence`}
                  size="small"
                  sx={{
                    height: 22, fontSize: 11,
                    bgcolor: `${confidenceColor}15`,
                    color: confidenceColor,
                    fontWeight: 600,
                  }}
                />
              )}
              {decision.processing_time && (
                <Chip
                  icon={<Speed sx={{ fontSize: 14 }} />}
                  label={`${decision.processing_time.toFixed(1)}s`}
                  size="small"
                  variant="outlined"
                  sx={{ height: 22, fontSize: 11 }}
                />
              )}
            </Box>
          </Box>

          {/* Decision summary */}
          <Typography variant="body2" fontWeight={500} sx={{ mb: 1 }}>
            {decision.decision}
          </Typography>

          {/* Confidence bar */}
          {decision.confidence != null && !compact && (
            <Box sx={{ mb: 1.5 }}>
              <LinearProgress
                variant="determinate"
                value={decision.confidence * 100}
                sx={{
                  height: 4, borderRadius: 2,
                  bgcolor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': { bgcolor: confidenceColor, borderRadius: 2 },
                }}
              />
            </Box>
          )}

          {/* Reasoning text */}
          {decision.reasoning && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, lineHeight: 1.7 }}>
              {decision.reasoning}
            </Typography>
          )}

          {/* Flags */}
          {decision.flags && decision.flags.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {decision.flags.map((flag, i) => (
                <Chip
                  key={i}
                  icon={decision.requires_human_review ? <Warning sx={{ fontSize: 14 }} /> : <CheckCircle sx={{ fontSize: 14 }} />}
                  label={flag.replace(/_/g, ' ')}
                  size="small"
                  variant="outlined"
                  color={decision.requires_human_review ? 'warning' : 'default'}
                  sx={{ height: 22, fontSize: 11 }}
                />
              ))}
            </Box>
          )}
        </Paper>
      </Collapse>
    </Box>
  );
}
