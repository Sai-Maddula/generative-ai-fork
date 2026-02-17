/**
 * Utility functions for calculating and displaying data freshness indicators
 */

/**
 * Calculate freshness status based on last analyzed timestamp
 * @param {string|null} lastAnalyzedAt - ISO timestamp of last analysis
 * @returns {object} Freshness status object with badge, color, and label
 */
export const getFreshnessStatus = (lastAnalyzedAt) => {
  if (!lastAnalyzedAt) {
    return {
      badge: 'never',
      color: '#9e9e9e', // gray
      label: 'Never analyzed',
      badgeIcon: '⚪',
      badgeText: 'Never'
    };
  }

  const now = new Date();
  const analyzedDate = new Date(lastAnalyzedAt);
  const hoursDiff = (now - analyzedDate) / (1000 * 60 * 60);
  const daysDiff = hoursDiff / 24;

  if (daysDiff < 1) {
    // Less than 24 hours - Fresh
    return {
      badge: 'fresh',
      color: '#2e7d32', // green
      label: 'Fresh data',
      badgeIcon: '🟢',
      badgeText: 'Fresh'
    };
  } else if (daysDiff < 7) {
    // 1-7 days - Aging
    return {
      badge: 'aging',
      color: '#ed6c02', // orange
      label: 'Data aging',
      badgeIcon: '🟡',
      badgeText: 'Aging'
    };
  } else {
    // 7+ days - Stale
    return {
      badge: 'stale',
      color: '#d32f2f', // red
      label: 'Stale data',
      badgeIcon: '🔴',
      badgeText: 'Stale'
    };
  }
};

/**
 * Format last analyzed timestamp as relative time
 * @param {string|null} lastAnalyzedAt - ISO timestamp of last analysis
 * @returns {string} Formatted relative time string
 */
export const formatLastAnalyzed = (lastAnalyzedAt) => {
  if (!lastAnalyzedAt) {
    return 'Never analyzed';
  }

  const now = new Date();
  const analyzedDate = new Date(lastAnalyzedAt);
  const diffMs = now - analyzedDate;
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);

  if (diffMinutes < 1) {
    return 'Just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  } else if (diffWeeks < 4) {
    return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`;
  } else {
    return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`;
  }
};

/**
 * Check if subscription analysis is stale (needs re-analysis)
 * @param {string|null} lastAnalyzedAt - ISO timestamp of last analysis
 * @param {number} staleThresholdDays - Days after which data is considered stale (default 7)
 * @returns {boolean} True if data is stale or never analyzed
 */
export const isAnalysisStale = (lastAnalyzedAt, staleThresholdDays = 7) => {
  if (!lastAnalyzedAt) {
    return true;
  }

  const now = new Date();
  const analyzedDate = new Date(lastAnalyzedAt);
  const daysDiff = (now - analyzedDate) / (1000 * 60 * 60 * 24);

  return daysDiff >= staleThresholdDays;
};
