# Copilot Instructions for AI Expense Advisor

## Purpose
These instructions define the required engineering and compliance standards for the AI Expense Advisor project. All work must align with the product requirements, architecture, design review, and implementation plan.

## Mandatory Rules

### 1. GDPR and data privacy compliance is non-negotiable
- Treat all personal financial data as sensitive personal data.
- Do not store, expose, or log unnecessary personal or financial information.
- Minimize data collection to what is required for the product feature being implemented.
- Support privacy-by-design principles throughout the application lifecycle.
- Ensure any new feature or API supports the retention, deletion, access, and portability expectations required for GDPR readiness.
- Never bypass consent, user-scoped access, or lawful processing requirements.
- Sensitive data in logs, traces, or AI prompts must be redacted or minimized before being recorded.

### 2. Follow the modular service architecture
- Keep the project organized by responsibility and clear boundaries.
- Maintain separation between:
  - API routes
  - service layer logic
  - data models and persistence
  - AI/retrieval orchestration
  - user and budget domain logic
- Do not place business logic directly inside route handlers when it belongs in a service layer.
- Favor small, testable functions and cohesive modules over large monolithic implementations.
- Keep domain logic reusable and independent of HTTP concerns.

### 3. Test coverage is required before any PR generation
- No pull request may be generated unless the relevant tests have been added or updated.
- Every new or changed behavior must have corresponding validation coverage.
- At minimum, tests should cover:
  - happy-path behavior
  - validation and error handling
  - edge cases relevant to the change
  - rules for privacy, data integrity, and user scoping
- Do not rely on reasoning alone; validate behavior with executable evidence.
- If a change is not testable, document why and include the risk before PR creation.

### 4. Security and data handling requirements
- Use user-scoped authorization for all financial data access.
- Do not expose data across users or accounts.
- Validate input and reject malformed or unsafe payloads.
- Support encryption for data in transit and at rest where supported by the deployment architecture.
- Keep audit trails for important financial and system events.
- Guard against overexposure of code, config, and secrets.

### 5. AI governance and financial safety
- AI-generated recommendations must be explainable and grounded in retrieved knowledge or user data.
- Do not present AI output as definitive financial advice without context and evidence.
- Ensure responses avoid harmful or misleading advice.
- Keep the decision trail visible where possible for debug and review.

### 6. Requirements and design traceability
- All implementation decisions should map back to the approved requirements and architecture decisions.
- Do not add speculative features outside the current milestone unless explicitly approved.
- If requirements change, update the relevant docs and affected tests before proceeding.

## Review and PR Standards
- Before generating any PR, confirm that:
  - the code is aligned with architecture and privacy standards
  - the affected behavior is covered by tests
  - the change is minimal, understandable, and documented
  - the implementation does not compromise security or compliance requirements
- PRs must include clear verification evidence and known limitations when relevant.

## Final Rule
When in doubt, prioritize privacy, correctness, maintainability, and verification over speed or convenience.
