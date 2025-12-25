# Feature Specification: Settings UI for API Key Management

**Feature Branch**: `010-settings-ui-api-keys`
**Created**: 2025-12-22
**Status**: Draft
**Input**: User description: "Settings tab UI for managing API keys (Gemini)"

## Clarifications

### Session 2025-12-24

- Q: How should the master encryption key be stored and managed for encrypting user API keys? → A: Store the encryption key in an environment variable (ENCRYPTION_KEY) with clear documentation for deployment
- Q: What specific API call should the Test Connection feature make to validate the Gemini API key? → A: Make a minimal text generation request with a 1-word prompt (e.g., "Hi") using generateContent endpoint
- Q: What database schema should be used for storing API keys? → A: Create a dedicated `user_api_keys` table with columns: id, user_id (FK), encrypted_key, provider (default 'gemini'), created_at, updated_at, last_validated_at, validation_status
- Q: What should be the default visibility state of the API key input field? → A: Input field is password-type (masked) by default with a "Show/Hide" toggle button (eye icon)
- Q: When the AI agent processes a chat request and the user has no configured API key, what should happen? → A: Hard fail: Return clear error prompting user to configure their API key in settings (with link). Do not use fallback global key.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Settings Tab (Priority: P1)

A user wants to configure their Gemini API key to enable AI-powered task management. They navigate to a dedicated Settings tab in the sidebar and see a clear interface for managing their API credentials.

**Why this priority**: This is the foundational infrastructure - users cannot configure API keys without a settings interface. This story alone provides the basic navigation and empty settings page, which is the minimum viable starting point.

**Independent Test**: Can be fully tested by clicking the Settings tab in the sidebar and verifying the settings page renders with proper layout and navigation. Delivers value by providing the access point to configuration features.

**Acceptance Scenarios**:

1. **Given** user is logged into the todo app, **When** they view the sidebar, **Then** they see a "Settings" tab/link alongside existing navigation items
2. **Given** user clicks the Settings tab, **When** the settings page loads, **Then** they see a settings interface with clear sections for API configuration
3. **Given** user is on the settings page, **When** they navigate to other tabs (Dashboard, Tasks), **Then** the Settings tab remains accessible and their settings are preserved
4. **Given** user accesses settings on desktop (≥768px), **When** the page renders, **Then** the layout uses appropriate spacing and readable text without horizontal scrolling
5. **Given** user accesses settings on mobile (<768px), **When** the page renders, **Then** the interface remains usable with touch-friendly controls and responsive layout

---

### User Story 2 - Enter and Save Gemini API Key (Priority: P1)

A user wants to provide their Gemini API key so the AI agent can process task management requests. They enter their API key in a secure input field, save it, and receive confirmation that their key is stored.

**Why this priority**: This is the core functionality - without the ability to save an API key, the AI agent cannot function. This delivers the primary value of the feature and enables AI-powered task management.

**Independent Test**: Can be fully tested by entering a valid Gemini API key, clicking Save, and verifying the key is persisted. Delivers immediate value by enabling AI agent functionality.

**Acceptance Scenarios**:

1. **Given** user is on the settings page, **When** they see the API key section, **Then** they find a labeled input field for "Gemini API Key" with a Save button
2. **Given** user enters a valid Gemini API key, **When** they click Save, **Then** the system stores the key securely and displays a success message (e.g., "API key saved successfully")
3. **Given** user has saved their API key, **When** they navigate away and return to settings, **Then** the API key input shows a masked version (e.g., "AIza...xyz") indicating a key is configured
4. **Given** user has saved their API key, **When** the AI agent processes chat requests, **Then** the agent uses this user-specific API key for Gemini API calls
5. **Given** user wants to update their API key, **When** they enter a new key and save, **Then** the new key replaces the old one and a confirmation message appears

---

### User Story 3 - Validate API Key Format and Connectivity (Priority: P1)

A user enters an API key but makes a typo or provides an invalid/expired key. The system validates the key format before saving and optionally tests connectivity to Gemini API, providing clear error messages if validation fails.

**Why this priority**: Validation prevents user frustration and ensures the AI agent can actually function with the provided key. This is critical for a smooth user experience and must be part of the initial implementation.

**Independent Test**: Can be fully tested by entering invalid keys (wrong format, expired, incorrect) and verifying appropriate error messages appear before saving. Delivers value by preventing configuration errors.

**Acceptance Scenarios**:

1. **Given** user enters an API key with incorrect format, **When** they attempt to save, **Then** the system displays an error message (e.g., "Invalid API key format. Gemini API keys typically start with 'AIza'")
2. **Given** user enters an API key, **When** they click "Test Connection" button, **Then** the system makes a lightweight API call to Gemini to verify the key works
3. **Given** the API key test succeeds, **When** the test completes, **Then** a success indicator appears (e.g., "✓ Connection successful")
4. **Given** the API key test fails, **When** the test completes, **Then** an error message explains the issue (e.g., "API key is invalid or expired. Please check your Gemini console.")
5. **Given** user has not entered any API key, **When** they try to use AI chat features, **Then** the system prompts them to configure their API key in settings with a direct link

---

### User Story 4 - View API Key Status and Usage (Priority: P2)

A user wants to know if their API key is properly configured and view basic status information. The settings page displays the key status (configured/not configured) and last validation timestamp.

**Why this priority**: Status visibility provides confidence and helps users troubleshoot issues, but the feature works without it. This enhances the P1 functionality but isn't required for basic operation.

**Independent Test**: Can be tested by saving an API key and verifying status indicators update correctly (configured/not configured, last tested timestamp). Delivers value by providing transparency.

**Acceptance Scenarios**:

1. **Given** user has not configured an API key, **When** they view settings, **Then** the status shows "Not Configured" with a clear call-to-action to add a key
2. **Given** user has saved a valid API key, **When** they view settings, **Then** the status shows "Configured" with a masked key preview (e.g., "AIza...xyz") and last saved timestamp
3. **Given** user's API key was validated successfully, **When** they view settings, **Then** they see a success indicator with timestamp (e.g., "✓ Last verified: Dec 22, 2025, 3:45 PM")
4. **Given** user's last API key test failed, **When** they view settings, **Then** they see a warning indicator with the error (e.g., "⚠ Last test failed: Invalid key")

---

### User Story 5 - Clear/Remove API Key (Priority: P2)

A user wants to remove their stored API key (for security reasons or to switch to a different provider in the future). They click a "Remove Key" button, confirm the action, and the key is deleted from storage.

**Why this priority**: Providing a way to remove keys is important for security and flexibility, but the feature functions without it initially. Users can overwrite keys by entering new ones.

**Independent Test**: Can be tested by saving a key, clicking "Remove Key", confirming, and verifying the key is deleted and status updates. Delivers value by giving users control over their credentials.

**Acceptance Scenarios**:

1. **Given** user has a configured API key, **When** they view settings, **Then** they see a "Remove Key" or "Clear Key" button next to the Save button
2. **Given** user clicks "Remove Key", **When** the button is clicked, **Then** a confirmation dialog appears asking "Are you sure you want to remove your API key? AI features will be disabled."
3. **Given** user confirms key removal, **When** they click "Confirm", **Then** the key is deleted from storage, status changes to "Not Configured", and a message appears (e.g., "API key removed")
4. **Given** user has removed their API key, **When** they try to use AI chat features, **Then** the system prompts them to configure a new key in settings

---

### Edge Cases

- **Empty API key submission**: What happens when user clicks Save with an empty API key field? System should display an error: "API key is required. Please enter your Gemini API key."
- **Very long API keys**: If user pastes an extremely long string (>500 characters), how does the system handle it? Should validate max length and show error if exceeded.
- **Special characters in API keys**: Gemini API keys may contain special characters. System must not strip or escape these incorrectly, which would break the key.
- **Concurrent key updates**: If user opens settings in two browser tabs and updates the key in both, how are conflicts resolved? Last save wins, with timestamp tracking to prevent race conditions.
- **API key storage security**: Where is the API key stored? Must use encrypted backend storage (database with encryption at rest) or secure environment variables, not localStorage or cookies in plaintext.
- **Session expiration during save**: If user's auth session expires while they're entering their API key, what happens? Should prompt re-authentication and preserve the entered (but unsaved) key in form state.
- **Network failure during Test Connection**: If connectivity test fails due to network issues (not key invalidity), how is this distinguished? Error message should clarify: "Connection test failed: Network error. Please check your internet connection."
- **API key revocation**: If user's Gemini API key is revoked/disabled after being saved, how does the system detect and notify them? AI agent should catch API errors and suggest re-checking settings.
- **Multiple users on shared device**: If multiple users share a device, how are API keys isolated? Keys are stored per authenticated user account in backend database, never shared.
- **Mobile keyboard covering input**: On mobile devices (<768px), when keyboard appears for API key input, does the Save button remain visible? Use appropriate viewport/scroll behavior to keep controls accessible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a "Settings" navigation item to the existing sidebar/navigation menu
- **FR-002**: Settings page MUST display a dedicated section for "Gemini API Key" configuration with clear labeling
- **FR-003**: System MUST provide a password-type input field for entering the Gemini API key (masked by default with bullets/dots to prevent shoulder-surfing)
- **FR-004**: System MUST include a "Show/Hide" toggle button (eye icon) next to the API key input that switches between password-type (masked) and text-type (visible) input
- **FR-005**: System MUST validate API key format before saving (Gemini keys typically start with "AIza" and have specific character patterns)
- **FR-006**: System MUST provide a "Save" button that persists the API key securely in the backend database
- **FR-007**: System MUST display a success message when the API key is saved successfully (e.g., toast notification or inline success text)
- **FR-008**: System MUST display clear error messages when API key validation fails, including format errors and connectivity issues
- **FR-009**: System MUST provide a "Test Connection" button that validates the API key by making a test request to Gemini API
- **FR-010**: System MUST display the API key status: "Not Configured", "Configured", or "Error" with appropriate visual indicators
- **FR-011**: System MUST mask stored API keys when displaying them (e.g., "AIza...xyz" showing only first 4 and last 3 characters)
- **FR-012**: System MUST associate API keys with the authenticated user's account (user-specific, not global configuration)
- **FR-013**: System MUST retrieve the user-specific API key when the AI agent processes chat requests and use it for Gemini API calls; if no key is configured, return error message: "Please configure your Gemini API key in Settings to use AI features" with clickable link to settings page
- **FR-014**: System MUST provide a "Remove Key" button to delete the stored API key with confirmation dialog
- **FR-015**: System MUST prevent saving empty or whitespace-only API keys with appropriate error message
- **FR-016**: Settings page MUST be responsive: usable on screens from 320px (mobile) to 2560px (desktop) with proper touch targets (≥44px) on mobile

### Non-Functional Requirements

- **NFR-001**: API keys MUST be stored encrypted in the backend database using a master ENCRYPTION_KEY environment variable (encryption at rest with AES-256 or Fernet)
- **NFR-002**: API key input field MUST use secure input practices (no browser autocomplete for sensitive fields, clear clipboard after paste)
- **NFR-003**: API key validation MUST complete within 3 seconds to provide timely feedback
- **NFR-004**: Test Connection feature MUST timeout after 10 seconds if Gemini API doesn't respond, with clear timeout message
- **NFR-005**: Settings page MUST load within 1 second for users with configured API keys
- **NFR-006**: API key save operation MUST be idempotent (multiple saves with same key produce same result)
- **NFR-007**: System MUST never log API keys in plaintext in application logs or error messages
- **NFR-008**: Settings UI MUST maintain 60fps scrolling performance even with form validation running

### Key Entities

- **UserApiKey** (table: `user_api_keys`): Represents a user's stored API key with schema:
  - `id` (UUID, primary key)
  - `user_id` (UUID, foreign key to users table, indexed)
  - `encrypted_key` (TEXT, encrypted API key value)
  - `provider` (VARCHAR, default 'gemini', supports future multi-provider scenarios)
  - `created_at` (TIMESTAMP)
  - `updated_at` (TIMESTAMP)
  - `last_validated_at` (TIMESTAMP, nullable)
  - `validation_status` (VARCHAR, nullable, values: 'success', 'failure', null)
  - Unique constraint: (user_id, provider) to enforce one key per provider per user
- **API Key Validation Result**: Ephemeral response object (not persisted separately) containing validation status (success/failure), error message (if failed), timestamp, and response time; validation_status and last_validated_at are stored in user_api_keys table

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate to Settings and save a valid Gemini API key in under 30 seconds
- **SC-002**: API key validation (format check) completes instantly (<100ms) on input blur or save attempt
- **SC-003**: Test Connection feature validates API key connectivity with Gemini API within 3 seconds
- **SC-004**: 95% of valid API key save attempts succeed on first try without errors
- **SC-005**: Settings page is fully usable on mobile devices (320px width) without layout issues or hidden controls
- **SC-006**: Zero instances of API keys being logged in plaintext or exposed in browser console/network tabs
- **SC-007**: Users can successfully update their API key and see changes reflected in AI agent behavior within 10 seconds
- **SC-008**: Error messages for invalid API keys are clear enough that 80% of users can self-correct without support
- **SC-009**: Settings page loads within 1 second for users returning to check their configuration
- **SC-010**: API key removal completes within 2 seconds with confirmation message displayed

## Dependencies *(mandatory)*

### Internal Dependencies

- **Authentication System (spec 004)**: Settings page requires user authentication to access and associate API keys with specific user accounts
- **AI Agent Backend (spec 008)**: The AI agent must be updated to retrieve user-specific API keys from the settings database when processing chat requests
- **Frontend Layout (spec 009)**: Settings tab integrates into the existing Next.js sidebar/navigation structure established in the chat integration spec
- **Backend API**: Requires new backend endpoints for API key CRUD operations (save, retrieve, test, delete) with user authentication

### External Dependencies

- **Gemini API**: Test Connection feature requires access to Google's Gemini API (https://generativelanguage.googleapis.com/v1beta/) to validate keys
- **Next.js Framework**: Settings page built as a Next.js route within the existing frontend structure
- **Database**: Requires new `user_api_keys` table with Alembic migration to store encrypted API keys with user associations (see Key Entities section for schema details)
- **Encryption Library**: Requires encryption library (e.g., cryptography in Python backend) for secure API key storage

## Assumptions *(mandatory)*

- **A-001**: Users have obtained their own Gemini API keys from Google AI Studio (https://aistudio.google.com/apikey)
- **A-002**: The backend has access to a master encryption key (ENCRYPTION_KEY environment variable) used to encrypt/decrypt all users' individual Gemini API keys at rest
- **A-003**: The existing authentication system (better-auth from spec 004) provides reliable user ID context for associating API keys
- **A-004**: Test Connection feature makes a minimal generateContent API call with a 1-word prompt (e.g., "Hi") to validate key functionality while minimizing token costs (typically <0.01 USD per test)
- **A-005**: Users understand they are responsible for their Gemini API usage costs and quotas
- **A-006**: The AI agent backend (spec 008) can be updated to require per-user API keys; users without configured keys receive clear error messages prompting them to configure settings (no fallback to global GEMINI_API_KEY)
- **A-007**: API keys are stored in the same PostgreSQL database used by the FastAPI backend (Neon serverless PostgreSQL)
- **A-008**: Only one API key per user is supported initially (not multiple keys or key rotation)
- **A-009**: API key format for Gemini follows Google's standard pattern (starts with "AIza", alphanumeric characters, specific length)

## Out of Scope *(optional)*

- **Multiple API Providers**: Settings only support Gemini API keys. OpenAI, Anthropic, or other LLM provider keys are not included.
- **API Key Rotation**: Automatic key rotation or expiration reminders are not implemented.
- **Usage Monitoring**: Tracking API usage, costs, or quota consumption is out of scope.
- **Key Sharing**: Users cannot share API keys with other users or teams.
- **API Key Import/Export**: No functionality to import keys from files or export for backup.
- **Advanced Security Features**: Features like IP whitelisting, key expiration policies, or audit logs are not included.
- **Settings History**: No tracking of previous API key values or change history.
- **Bulk Configuration**: No admin interface for configuring API keys for multiple users at once.
- **Custom API Endpoints**: Users cannot configure custom Gemini API endpoints or proxy URLs.
- **Key Permissions**: No granular permissions for what each API key can do (all keys have full access).

## Constraints *(optional)*

- **Security Constraint**: API keys MUST be encrypted at rest in the database. Plaintext storage is not acceptable.
- **Authentication Constraint**: Settings page MUST require user authentication. Anonymous users cannot access or configure API keys.
- **UI Constraint**: Settings tab must integrate into the existing sidebar navigation without requiring major layout redesign.
- **Backend Constraint**: Must use the existing FastAPI backend (spec 003) for API key storage and retrieval endpoints.
- **Database Constraint**: Must use the existing Neon PostgreSQL database (shared with FastAPI and auth server) for API key storage.
- **Performance Constraint**: API key retrieval must not add >50ms latency to AI agent chat request processing.
- **Browser Support Constraint**: Must support last 2 versions of Chrome, Firefox, Safari, and Edge (no IE11 support).

## Risks *(optional)*

### Risk 1: API Key Security Vulnerabilities

**Description**: Storing user API keys introduces significant security risk. If encryption is implemented incorrectly, keys could be compromised, leading to unauthorized API usage and potential financial impact for users.

**Impact**: Critical - Key compromise could lead to unauthorized API usage, user trust loss, potential legal liability

**Mitigation**:
- Use well-tested encryption libraries (e.g., Python's cryptography with Fernet or AES-256)
- Store encryption keys in environment variables or dedicated secrets manager (not in code)
- Implement encrypted database columns using SQLAlchemy's encryption features
- Never log API keys in plaintext
- Add security testing to validate encryption implementation
- Consider using hardware security modules (HSM) for production encryption keys

**Contingency**: If encryption implementation is found to be vulnerable, immediately disable API key storage, notify users to rotate their Gemini keys, and implement proper encryption before re-enabling the feature

---

### Risk 2: Gemini API Key Format Changes

**Description**: Google may change the format of Gemini API keys in the future, breaking our validation logic and preventing users from saving new keys.

**Impact**: Medium - Users cannot configure new keys, but existing keys continue working

**Mitigation**:
- Use flexible validation that checks basic patterns without being overly strict
- Make validation patterns configurable via backend constants (easy to update)
- Monitor Gemini API documentation for format changes
- Provide a "Skip Validation" option for edge cases (with warning)

**Contingency**: If key format changes, push a backend update to adjust validation patterns. Provide clear error messages directing users to settings documentation.

---

### Risk 3: Test Connection Feature Abuse

**Description**: Users could spam the "Test Connection" button, causing excessive API calls to Gemini, potentially hitting rate limits or incurring costs.

**Impact**: Low-Medium - Could cause rate limiting errors or increased operational costs

**Mitigation**:
- Implement client-side rate limiting (disable button for 5 seconds after test)
- Add backend rate limiting per user (max 5 tests per hour)
- Use minimal token consumption for test requests (e.g., single word prompt)
- Cache test results for 1 hour (if key hasn't changed, show cached result)

**Contingency**: If abuse is detected, add stricter rate limits or remove the Test Connection feature, relying only on format validation and runtime error handling

---

### Risk 4: Backend Update Complexity for Per-User Keys

**Description**: Updating the AI agent backend (spec 008) to use per-user API keys instead of a global key may be more complex than anticipated, potentially requiring significant refactoring.

**Impact**: High - Could delay the feature or block AI agent functionality if implemented incorrectly

**Mitigation**:
- Design a clear backend service layer for API key retrieval with explicit error handling for missing keys
- Create comprehensive integration tests for per-user key lookup and missing-key error scenarios
- Implement clear error messages with direct links to settings page when users attempt AI features without configured keys
- Phase implementation: first add storage and settings UI, then update agent to require stored keys
- Provide migration guide/announcement for existing users to configure their API keys

**Contingency**: If per-user key requirement creates too much user friction initially, add a temporary admin-controlled feature flag to allow a grace period where missing keys show persistent warnings but don't block usage. Remove grace period after user adoption reaches 80%.

## Related Documentation *(optional)*

- **Spec 008 (OpenAI Agents SDK Integration)**: Describes the AI agent that will use the configured Gemini API keys
- **Spec 004 (Auth Server)**: Provides authentication context for associating API keys with user accounts
- **Spec 009 (Frontend Chat Integration)**: Describes the chat UI that depends on properly configured API keys
- **Google AI Studio**: Official documentation for obtaining Gemini API keys (https://aistudio.google.com/apikey)

## Notes *(optional)*

- **User Guidance**: Consider adding help text or links in the settings page explaining how to obtain a Gemini API key from Google AI Studio
- **Future Enhancements**: This spec focuses on Gemini keys. Future iterations could support multiple LLM providers (OpenAI, Anthropic, etc.) with provider selection UI
- **Cost Transparency**: Consider adding a warning message that users are responsible for their own API usage costs when using Gemini
- **Accessibility**: Ensure settings form meets WCAG 2.1 AA standards (keyboard navigation, screen reader support, clear labels, proper focus management)
- **Analytics**: Track settings page visits, API key save success/failure rates, and test connection usage to identify UX improvements
- **Testing Strategy**: Integration tests should verify encryption/decryption round-trip, API key retrieval in agent requests, and error handling for missing/invalid keys
