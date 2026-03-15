
# TESTING_APPROACH #

## System Understanding

The system is a small vulnerability management platform composed of two main services:

- Scanner Service - manages assets and runs scans.

- Dashboard API + UI - exposes findings and allows managing their status.

The basic flow of the system is:

`Asset → Scan → Findings → Vulnerabilities`

A scan is triggered on an asset with a list of vulnerability IDs.
The scan produces findings which are stored in PostgreSQL and later managed via the Dashboard API and UI.

## Testing Strategy

Because the system contains multiple components, I separated tests by layer so failures are easier to diagnose.

Tests are organized into:

- `tests/api`
- `tests/db`
- `tests/integration`
- `tests/ui`

### API tests

Validate the main findings lifecycle:

- create finding
- get finding
- update status
- dismiss finding

### DB tests

Sanity checks that API actions actually persist changes in the database (for example status updates or dismiss flags).

### Integration tests

End-to-end flow across services:

`create asset → run scan → verify findings appear`

This verifies that the scanner service and dashboard API work together.

### UI tests

A minimal smoke test that verifies the UI loads and connects to the backend.

## Test Structure

Tests aim to stay small and readable.

A typical test follows a simple flow:

`arrange → act → assert`

Shared helpers live in test_support/:

- `data.py` – payload builders
- `extract.py` – response helpers
- `assertions.py` – common assertions

API calls are wrapped in simple clients to avoid repeating request logic across tests.

## Limitations / What Did Not Go Well Enough

Due to the time constraint of the assignment, some areas are lighter than they would be in a production automation suite.

For example:

- Some tests stop at status-code validation instead of validating deeper business behavior.
- Some DB tests rely on existing data instead of creating their own test data.
- A few fixtures derive IDs from the environment, which makes runs less deterministic.
- The UI smoke test mostly validates connectivity rather than UI behavior.
- The scan integration test also mixes several concerns (scan execution, polling, validation) which would normally be separated.

## How I Would Design the Test Framework With More Time

The biggest improvement would be clearer separation of responsibilities between layers.

Tests themselves should remain small and describe the scenario only.

Other responsibilities should live in dedicated layers.

For example:

```
tests
↓
domain helpers
↓
API clients
↓
DB helpers
DB access layer
```

Tests should not contain raw SQL queries.

Instead of writing SQL directly inside tests like:

```sql
SELECT status FROM findings WHERE id = ...
```

tests would call a small helper such as:

`db_findings.get_status(finding_id)`

This keeps tests readable and prevents database logic from leaking into the test layer.

### Test data factories

Instead of relying on existing data in the environment, tests should create their own entities.

Example fixtures:

- `asset_factory`
- `finding_factory`
- `vulnerability_factory`

Each test would create the data it needs and the fixture would handle cleanup.

### Reusable async helpers

Polling logic (used when waiting for findings after a scan) should live in a shared helper with consistent timeout and error reporting.

### Slightly richer API clients

API clients could also provide better debugging support:

- request logging
- structured response parsing
- clearer failure messages

## Summary

The current suite focuses on validating the main system flow end-to-end:

- scan execution
- finding lifecycle
- persistence in the database

Given the limited time of the assignment, the focus was on validating the system behavior rather than building a full production-grade automation framework.

With more time I would mainly improve:

* deterministic test data
* clearer separation of responsibilities
* reusable helpers for async flows
* slightly richer client and DB helper layers