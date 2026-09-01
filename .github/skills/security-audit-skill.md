# Security Audit Skill

## Purpose
This skill defines minimum security expectations for code review, implementation, and validation in this project. It is intended to prevent insecure handling of user input, secrets, authentication tokens, and database configuration.

## Core Rules

### 1. Input Sanitization
- Treat all user-controlled input as untrusted.
- Validate input at the boundary of the application before it reaches business logic or storage.
- Enforce type, length, format, and allowed-value checks for all request fields.
- Reject unexpected or malformed payloads with explicit validation errors.
- Strip or escape unsafe content when it is rendered into HTML, logs, or downstream systems.
- Never concatenate untrusted strings directly into SQL, shell commands, file paths, or URLs.
- Prefer parameterized queries, typed models, and schema validation over ad hoc string assembly.
- Log sanitization failures without exposing sensitive data.

### 2. OAuth Token Handling
- Never hardcode OAuth client secrets, access tokens, refresh tokens, or API keys in source code.
- Store tokens only in environment variables, secure secret stores, or managed cloud secret systems.
- Use short-lived tokens whenever possible and refresh them through approved flows.
- Validate token expiry, audience, issuer, and scopes before trusting them.
- Reject tokens with missing or unexpected claims.
- Ensure token values are never logged, echoed in responses, or included in stack traces.
- Encrypt tokens at rest if they must be persisted, and limit retention windows.
- Use secure redirect URIs and validate callback state to prevent CSRF and token leakage.

### 3. Secure Database Connection Strings
- Never commit database credentials to version control.
- Load connection strings from environment variables or a secure configuration manager.
- Use TLS/SSL for all remote database connections unless the environment explicitly requires insecure local-only development.
- Ensure the connection string never contains plaintext credentials in logs, errors, or debug output.
- Prefer least-privilege database users with minimal required permissions.
- Separate read-only, write, and admin access roles where appropriate.
- Redact credentials in any diagnostics, health checks, or startup logs.
- Validate configuration at startup and fail fast if required database settings are missing or invalid.

## Review Checklist
When reviewing or implementing code, verify the following:
- Input validation exists for all public endpoints and external data sources.
- Secrets are not embedded in source, configs, or logs.
- OAuth flows use secure token lifecycle handling and scope validation.
- Database connection settings are externalized and redacted.
- Sensitive failures are handled without leaking secrets or internal details.

## Enforcement Expectations
- Any code that violates these rules must be treated as a security issue.
- Security problems should be fixed before merging or generating a PR.
- If a requirement is unclear, prefer the more restrictive and safer option.

## Required Response Style for Assistants
When generating code or review feedback, explicitly call out:
- the exact security risk,
- the relevant file or code path,
- the recommended mitigation,
- and the expected safe pattern to follow.
