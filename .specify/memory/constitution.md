<!--
Sync Impact Report
- Version change: unratified scaffold -> 1.0.0
- Modified principles: none; all five principles established from the scaffold
- Added sections: Security and Data Handling; Development Workflow
- Removed sections: none
- Follow-up TODOs: RATIFICATION_DATE requires confirmation of the original adoption date
-->

# Azure Storage Handler Constitution

## Core Principles

### I. Clear Contracts
Components MUST expose small, explicit contracts with documented inputs, outputs, and failure
behavior. Public interfaces MUST avoid leaking storage-provider details unless those details are
part of the intended contract. Rationale: stable boundaries make storage behavior testable and
allow implementations to evolve without forcing unrelated callers to change.

### II. Correctness and Data Integrity
Operations that read, write, move, or delete data MUST preserve the documented data and metadata
semantics. Code MUST define behavior for missing resources, retries, partial failures, duplicate
requests, and concurrency where those cases are possible. Rationale: storage bugs can silently
lose or corrupt data and are more costly than explicit failures.

### III. Testable Changes
Every behavior change MUST include focused automated tests for the changed contract. Tests MUST
cover successful behavior and relevant failure paths; integration tests MUST be added when the
change depends on an actual storage service, serialization format, authentication flow, or
cross-component contract. Rationale: tests provide executable evidence that storage behavior is
correct and remains correct during refactoring.

### IV. Secure by Default
Code MUST minimize permissions, protect secrets, validate untrusted inputs, and avoid logging
credentials or sensitive payloads. Configuration MUST be externalized from source code, and
security-sensitive defaults MUST fail closed. Rationale: storage handlers commonly operate on
business data and credentials, so insecure convenience defaults create disproportionate risk.

### V. Observable and Operationally Simple
Failures MUST provide actionable, structured context without exposing sensitive data. External
calls SHOULD have bounded timeouts and an explicit retry policy where retries are safe. New
abstractions, dependencies, and configuration knobs MUST be justified by a concrete requirement.
Rationale: predictable diagnostics and minimal complexity reduce operational cost and failure
amplification.

## Security and Data Handling

The implementation MUST follow the principle of least privilege for Azure resources and local
development identities. Secrets MUST be supplied through supported environment or secret-store
configuration and MUST NOT be committed to the repository. Data retention, access logging, and
encryption requirements MUST be documented when the feature handles regulated or sensitive data.

## Development Workflow

Changes MUST be traceable to a feature specification or issue. Before review, the author MUST
run the narrowest relevant automated tests and static checks, then record any unavailable checks
and their residual risk. Reviews MUST verify contract compatibility, error handling, security,
and test coverage. Deployments MUST use reviewed configuration and MUST NOT rely on untracked
local state.

## Governance

This constitution is the highest-level engineering policy for the project. When another practice
conflicts with it, the conflict MUST be resolved in favor of this document or explicitly amended.

Amendments require a documented rationale, an update to the version and amendment date, and a
review of affected specifications, plans, tasks, and implementation guidance. Versioning follows
Semantic Versioning: MAJOR for incompatible governance changes or principle removals, MINOR for
new principles or materially expanded requirements, and PATCH for clarifications and non-semantic
wording changes. Every feature review MUST check compliance with the applicable principles; any
waiver MUST be recorded with an owner, rationale, and expiration or follow-up date.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-09-23
