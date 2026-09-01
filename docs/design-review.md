# AI Expense Advisor — Design Review

## Review Scope
This review evaluates the proposed architecture described in [docs/architecture.md](architecture.md) for risks related to handling sensitive financial data, GDPR compliance, AI governance, and general system security.

## Executive Decision
Status: Conditional approval pending security and compliance remediation.

The architecture is directionally strong and suitable for an MVP, but it does not yet define the minimum controls required for handling personal financial data in a compliant and secure manner. The main risks are privacy, unauthorized access, unsafe AI-generated financial advice, and insufficient compliance lifecycle controls.

---

## Summary of Findings

### 1. Critical: Sensitive financial data is not yet protected by a defined privacy and compliance model
The architecture mentions PostgreSQL, AI classification, and RAG, but it does not explicitly define:
- lawful basis for processing personal financial data under GDPR
- consent management and notice language for users
- data minimization rules for what is stored and retained
- support for data subject rights: access, rectification, restriction, deletion, and portability
- retention schedules for transactions, alerts, and AI interaction logs

Risk:
Financial data is highly personal. Without explicit compliance controls, the application may be non-compliant with GDPR and expose the project to legal and reputational risk.

Decision:
Add a formal privacy design section before implementation. Define the legal basis, retention policy, user consent model, and deletion workflow. Treat personal financial records as personal data requiring explicit governance.

---

### 2. High: Access control and tenant isolation are under-specified
The architecture describes services and databases, but it does not specify:
- authentication mechanism for users and admin roles
- authorization model for per-user data access
- multitenancy or user isolation rules
- session security and token handling
- MFA or elevated security controls for sensitive operations

Risk:
Without strict per-user isolation, one user could access another user’s data by mistake or due to a broken query or routing bug. This is especially critical in finance systems.

Decision:
Mandate user-scoped authorization by default. Every transaction, budget, and alert query must be enforced by user identity. Add RBAC for admin functions and secure token handling with short-lived credentials and refresh flows.

---

### 3. High: Sensitive fields and AI data handling are not sufficiently protected
The design includes AI categorization and RAG for financial advice, but it does not state how raw transaction descriptions, merchant names, or user queries are protected when sent to an LLM or vector pipeline.

Missing controls include:
- data classification of raw financial data
- redaction or tokenization of personal identifiers before model inference
- contract review of model provider data-use policies
- explicit prohibition on sending user financial data to third-party services without approval
- AI safety constraints for financial recommendations

Risk:
Model providers may retain or use prompts and embeddings; raw financial data could be exposed or used beyond the user’s intent. AI-generated advice could also be inaccurate or unsafe when acting on personal finance decisions.

Decision:
Use a strict data governance policy for AI. Redact or minimize sensitive user data before invoking external models. Prefer internal or approved model providers with clear data handling terms. Require grounded responses and evidence-based explanations when generating financial advice.

---

### 4. High: AI financial advice lacks governance and risk controls
The architecture proposes a recommendation engine, but it does not define:
- validation of model outputs before presentation to users
- explainability requirements for recommendations
- guardrails against overconfident or harmful financial guidance
- human review for high-risk financial decisions
- fallback behavior when model retrieval or classification fails

Risk:
AI-generated financial advice can be misleading or harmful if it gives budget advice without enough evidence or fails to distinguish user-specific context from generic guidance.

Decision:
Require grounded outputs. Recommendations must cite retrieved knowledge and relevant transaction context. The system should present suggestions as advisory and informative, not definitive financial advice. High-risk outputs should be flagged or escalated for review.

---

### 5. Medium: Encryption and key management are not yet explicit
The architecture states that privacy should be respected, but it does not define:
- encrypted storage for database data
- TLS requirements for all external and internal traffic
- secret management for credentials and API tokens
- key rotation and ownership responsibilities

Risk:
A finance system without explicit encryption and secret management puts sensitive data at risk in transit and at rest.

Decision:
Adopt encryption in transit with TLS 1.2+ and encryption at rest where supported by the platform. Store secrets in a managed secret store or KMS, not in source code or config files.

---

### 6. Medium: Operational logging and audit trails are insufficient for compliance and incident response
The architecture mentions logging, but there is no clear policy for:
- structured audit trails for user activity and financial modifications
- ability to trace which user changed data or triggered an alert
- log retention and secure storage of sensitive operational events
- redaction of personally identifiable or payment-related data in logs

Risk:
Without adequate logs, security incidents and compliance investigations become difficult or impossible.

Decision:
Add auditable event logs for transaction creation, budget change, alert generation, admin updates, and AI recommendation generation. Ensure logs are immutable enough for investigations and redact sensitive payloads before storage.

---

### 7. Medium: No explicit security testing or threat model is defined
There is no mention of:
- OWASP application security controls
- rate limiting and abuse protections
- input validation beyond schema checks
- protection against injection, mass assignment, broken object-level authorization, and enumeration attacks
- secure secret rotation and dependency monitoring

Risk:
The application exposes financial and user data surfaces that are common targets for abuse, especially when APIs are involved.

Decision:
Add a lightweight threat model and security test plan before the first production release, including dependency scanning, API abuse limits, role validation, and regular security review of third-party integrations.

---

## Architectural Gaps to Address Before Production

1. Privacy and compliance specification
   - Define GDPR processing purposes, consent, retention, and deletion lifecycle.
2. Explicit security baseline
   - Add auth, authz, encryption, rate limiting, and audit logging.
3. AI governance
   - Redact sensitive data before model calls and require explainable recommendations.
4. Data minimization and retention
   - Store only required fields and define retention windows for logs and vectors.
5. Secure operations
   - Add backup, restore, and incident-response readiness plans.
6. Quality assurance for sensitive data
   - Include security and privacy testing in the verification stage.

---

## Decisions and Remediation Plan

### Decision 1: Treat the application as a personal-data system
All transaction, budget, and user interaction data will be handled under a privacy-first design. This includes clear consent, minimal data retention, and deletion support.

### Decision 2: Require per-user authorization and strict data isolation
Every API call must validate the current user’s identity and restrict results to that user’s scope.

### Decision 3: Add encryption and secret management controls
Data in transit must use TLS, secrets must be stored in a secret manager, and encryption at rest must be enabled where supported.

### Decision 4: Use explainable and grounded AI outputs
RAG and model-generated advice must be traceable to retrieved knowledge and user-specific transaction context, not just free-form LLM output.

### Decision 5: Formalize compliance workflow for GDPR
Implementation must include a user data access/deletion process and retention policy for all personal data and logs.

### Decision 6: Add security review as a release gate
The architecture should not be considered production-ready without a documented security review and compliance checklist.

---

## Final Review Outcome
The current architecture is a solid MVP foundation for a personal finance assistant, but it is not yet sufficient for secure production handling of sensitive financial data. The project should proceed only with explicit remediation on privacy, access control, encryption, AI governance, and compliance-driven data lifecycle controls.

This is not a blocker to architecture iteration, but it is a required gate before deployment.
