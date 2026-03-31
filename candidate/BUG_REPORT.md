# Bug Report

## 1. SQL Injection In Findings Search

- Title: `/findings/search` is vulnerable to SQL injection
- Severity: Critical
- Steps to reproduce:
  1. Send a request to `GET /findings/search?q=' OR '1'='1`
  2. Observe the returned results
- Expected behavior:
  - The query should be treated as plain text input and only return exact substring matches
  - The endpoint should use parameterized SQL and must not alter query semantics based on user input
- Actual behavior:
  - The endpoint builds raw SQL with f-string interpolation
  - Injection-like input can change the SQL behavior and may return unintended rows

## 2. Dismissed Finding Is Still Accessible By Detail Endpoint

- Title: Dismissed finding still returns from `GET /findings/{id}`
- Severity: High
- Steps to reproduce:
  1. Create a finding
  2. Dismiss it with `DELETE /findings/{id}`
  3. Call `GET /findings/{id}`
- Expected behavior:
  - Dismissed findings should be hidden from standard retrieval and return `404`
- Actual behavior:
  - The detail endpoint still returns the dismissed record

## 3. Asset Pagination Skips The First Record

- Title: `GET /assets` has an off-by-one pagination defect
- Severity: High
- Steps to reproduce:
  1. Call `GET /assets?page=1&per_page=10`
  2. Compare the returned rows with the database ordered by `id`
- Expected behavior:
  - The first page should start from the first active asset
- Actual behavior:
  - The implementation offsets by `+1`, so the first asset is skipped

## 4. Concurrent Scans Create Duplicate Findings

- Title: Concurrent or repeated scans create duplicate findings for the same asset and vulnerability
- Severity: High
- Steps to reproduce:
  1. Run two scans for the same `asset_id` and same `vulnerability_ids`
  2. Check rows in `findings`
- Expected behavior:
  - The system should deduplicate or prevent duplicate active findings for the same asset and vulnerability
- Actual behavior:
  - Multiple findings are created because there is no uniqueness check in service logic or DB constraint

## 5. UI Does Not Refresh Finding Status After Update

- Title: Finding status change through UI shows success message but does not refresh the row
- Severity: Medium
- Steps to reproduce:
  1. Open `http://localhost:8000/`
  2. Change a finding status via the dropdown
  3. Observe the row and summary cards
- Expected behavior:
  - The row status and summary cards should update after a successful change
- Actual behavior:
  - A success message is shown, but the row and summary are not refreshed

## 6. Invalid Finding Status Transitions Are Allowed

- Title: API allows invalid finding lifecycle transitions
- Severity: Medium
- Steps to reproduce:
  1. Create or locate a resolved or false-positive finding
  2. Update it to another status such as `open` or `confirmed`
- Expected behavior:
  - Invalid backward or unsupported transitions should be rejected
- Actual behavior:
  - The API allows arbitrary status changes as long as the status value is valid

## 7. No CVSS Score Range Constraint

- Title: Database does not enforce valid CVSS score range for vulnerabilities
- Severity: Medium
- Steps to reproduce:
  1. Attempt to insert a vulnerability record with `cvss_score = 11.5`
  2. Observe whether PostgreSQL accepts the row
- Expected behavior:
  - The database should reject CVSS values outside the valid `0.0` to `10.0` range
- Actual behavior:
  - No effective range constraint is present, so invalid CVSS scores may be accepted
