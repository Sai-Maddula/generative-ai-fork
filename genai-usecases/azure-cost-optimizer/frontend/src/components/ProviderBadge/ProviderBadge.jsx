import React from 'react';
import { Chip, Tooltip } from '@mui/material';
import CloudIcon from '@mui/icons-material/Cloud';

/**
 * ProviderBadge Component
 *
 * Displays a cloud provider badge with appropriate styling and icon.
 * Supports Azure, AWS, and GCP.
 */
const ProviderBadge = ({ provider, size = 'small', showIcon = true }) => {
  // Provider configuration
  const providerConfig = {
    azure: {
      label: 'Azure',
      color: '#0078D4',
      bgColor: '#E6F2FF',
      icon: '🔷',
      tooltip: 'Microsoft Azure'
    },
    aws: {
      label: 'AWS',
      color: '#FF9900',
      bgColor: '#FFF4E6',
      icon: '🟧',
      tooltip: 'Amazon Web Services'
    },
    gcp: {
      label: 'GCP',
      color: '#4285F4',
      bgColor: '#E8F0FE',
      icon: '🔴',
      tooltip: 'Google Cloud Platform'
    }
  };

  const normalizedProvider = provider ? provider.toLowerCase() : 'azure';
  const config = providerConfig[normalizedProvider] || providerConfig.azure;

  const chipLabel = showIcon ? `${config.icon} ${config.label}` : config.label;

  return (
    <Tooltip title={config.tooltip} arrow>
      <Chip
        label={chipLabel}
        size={size}
        sx={{
          backgroundColor: config.bgColor,
          color: config.color,
          fontWeight: 600,
          border: `1px solid ${config.color}40`,
          '& .MuiChip-label': {
            px: 1.5,
          },
        }}
      />
    </Tooltip>
  );
};

export default ProviderBadge;
