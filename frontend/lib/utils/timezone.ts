// Timezone detection utility
// Spec: 009-frontend-chat-integration

/**
 * Get the user's current timezone using the browser's Intl API
 * @returns IANA timezone string (e.g., "America/New_York", "Europe/London")
 */
export function getUserTimezone(): string {
  try {
    // Use Intl API to get browser's timezone
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Validate that we got a non-empty string
    if (!timezone || timezone.length === 0) {
      throw new Error('Empty timezone returned from Intl API');
    }

    return timezone;
  } catch (error) {
    // Fallback to UTC if Intl API fails (should never happen in modern browsers)
    console.error('Failed to detect timezone, falling back to UTC:', error);
    return 'UTC';
  }
}
