import React from 'react';
import { Chip, Tooltip } from '@mui/material';
import { getFreshnessStatus } from '../../utils/freshnessUtils';

/**
 * FreshnessBadge Component
 * Displays a color-coded badge indicating data freshness
 *
 * @param {string|null} lastAnalyzedAt - ISO timestamp of last analysis
 * @param {string} size - 'small' or 'medium' (default: 'small')
 */
const FreshnessBadge = ({ lastAnalyzedAt, size = 'small' }) => {
  const freshness = getFreshnessStatus(lastAnalyzedAt);

  return (
    <Tooltip title={freshness.label} arrow>
      <Chip
        label={freshness.badgeText}
        size={size}
        sx={{
          backgroundColor: freshness.color,
          color: '#fff',
          fontWeight: 600,
          fontSize: size === 'small' ? '0.7rem' : '0.75rem',
          height: size === 'small' ? '20px' : '24px',
          '& .MuiChip-label': {
            px: 1,
          },
        }}
      />
    </Tooltip>
  );
};

export default FreshnessBadge;
