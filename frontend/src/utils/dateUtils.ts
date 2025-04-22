/**
 * Date utility functions
 */

/**
 * Format a date string or Date object to a human-readable date and time
 */
export const formatDateTime = (dateString?: string | Date | null): string => {
  if (!dateString) return 'N/A';
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/**
 * Format a date string or Date object to a human-readable date
 */
export const formatDate = (dateString?: string | Date | null): string => {
  if (!dateString) return 'N/A';
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Format a date string or Date object to a human-readable time
 */
export const formatTime = (dateString?: string | Date | null): string => {
  if (!dateString) return 'N/A';
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid time';
  }
  
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/**
 * Format a duration in seconds to a human-readable string
 */
export const formatDuration = (seconds?: number | null): string => {
  if (seconds === undefined || seconds === null) return 'N/A';
  
  if (seconds < 60) {
    return `${seconds.toFixed(2)} seconds`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return `${hours}h ${remainingMinutes}m ${remainingSeconds.toFixed(0)}s`;
};

/**
 * Get a relative time string (e.g., "2 hours ago", "in 3 days")
 */
export const getRelativeTimeString = (dateString?: string | Date | null): string => {
  if (!dateString) return 'N/A';
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  const now = new Date();
  const diffInSeconds = Math.floor((date.getTime() - now.getTime()) / 1000);
  
  // Future date
  if (diffInSeconds > 0) {
    if (diffInSeconds < 60) return `in ${diffInSeconds} seconds`;
    if (diffInSeconds < 3600) return `in ${Math.floor(diffInSeconds / 60)} minutes`;
    if (diffInSeconds < 86400) return `in ${Math.floor(diffInSeconds / 3600)} hours`;
    if (diffInSeconds < 2592000) return `in ${Math.floor(diffInSeconds / 86400)} days`;
    if (diffInSeconds < 31536000) return `in ${Math.floor(diffInSeconds / 2592000)} months`;
    return `in ${Math.floor(diffInSeconds / 31536000)} years`;
  }
  
  // Past date
  const absDiff = Math.abs(diffInSeconds);
  if (absDiff < 60) return `${absDiff} seconds ago`;
  if (absDiff < 3600) return `${Math.floor(absDiff / 60)} minutes ago`;
  if (absDiff < 86400) return `${Math.floor(absDiff / 3600)} hours ago`;
  if (absDiff < 2592000) return `${Math.floor(absDiff / 86400)} days ago`;
  if (absDiff < 31536000) return `${Math.floor(absDiff / 2592000)} months ago`;
  return `${Math.floor(absDiff / 31536000)} years ago`;
};
