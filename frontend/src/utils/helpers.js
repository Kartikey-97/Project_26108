/**
 * Global Helper Utilities for ProcureIntel BIS Recommendation Engine
 */

// Format ISO date string into readable format (e.g. 22 Aug 2026)
export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

// Format percentage with 1 decimal place if needed
export function formatScore(score) {
  if (score === undefined || score === null) return '0%';
  return `${typeof score === 'number' ? score.toFixed(0) : score}%`;
}

// Map status code to human-readable label
export function getStatusText(status) {
  switch (status) {
    case 'COMPLETED':
      return 'Completed';
    case 'WARNING_FLAGGED':
      return 'Flagged Clause';
    case 'IN_REVIEW':
      return 'In Review';
    case 'CURRENT':
      return 'Current Standard';
    case 'AMENDED':
      return 'Amended Standard';
    case 'SUPERSEDED':
      return 'Superseded Standard';
    default:
      return status;
  }
}

// Truncate text cleanly with ellipsis
export function truncateText(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}
