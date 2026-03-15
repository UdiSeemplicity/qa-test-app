# Bug Report #

Quick notes from testing:

---

## Bug 1: Dismissed finding still accessible by ID

**Severity:** Medium

**Endpoint / Area:** `GET /findings/{finding_id}`

**Steps to reproduce**
1. Create a finding (`POST /findings`).
2. Dismiss it (`DELETE /findings/{finding_id}`).
3. Fetch it (`GET /findings/{finding_id}`).

**Expected**
Dismissed finding is not retrievable (404) / hidden consistently

**Actual**
Returns 200 + finding details

---

## Bug 2: Finding status allows invalid transitions

**Severity:** High

**Endpoint / Area:** `PUT /findings/{finding_id}/status`

**Steps to reproduce**
1. Create a finding.
2. Set status to `resolved`.
3. Set status back to `open`.

**Expected**
Invalid transitions rejected (400). Only allow defined flow (e.g. `open → confirmed → in_progress → resolved`).

**Actual**
Any status change is accepted as long as the value is in the allowed list

---

## Bug 3: SQL injection in findings search

**Severity:** Critical

**Endpoint / Area:** `GET /findings/search`

**Steps to reproduce**
1. Call `GET /findings/search?q=%27%20OR%201%3D1%20--`.
2. Observe it runs and returns results.

**Expected**
Search uses parameterized SQL. Input treated as data.

**Actual**
Raw SQL is built via string interpolation

---

## Bug 4: CVSS score has no DB range constraint

**Severity:** Medium

**Endpoint / Area:** DB schema (`vulnerabilities.cvss_score`)

**Steps to reproduce**
1. Insert a vulnerability with `cvss_score = 999` (or `-1`).
2. Query it back.

**Expected**
DB rejects values outside 0–10 (or allows NULL only)

**Actual**
Invalid scores are stored

---

## Bug 5: Risk score returns float noise / no rounding

**Severity:** Low

**Endpoint / Area:** `GET /stats/risk-score`

**Steps to reproduce**
1. Have a few active findings with fractional CVSS.
2. Call `GET /stats/risk-score`

**Expected**
Rounded values (clear policy).
Stable output

**Actual**
Raw float math. Can return long decimals (e.g. `6.69999999997`)

---

## Bug 6: Assets pagination skips first row

**Severity:** Medium

**Endpoint / Area:** Scanner Service `GET /assets`

**Steps to reproduce**
1. Have > `per_page` assets
2. Call `GET /assets?page=1&per_page=10`
3. Notice the first asset is missing

**Expected**
Page offset should be `(page - 1) * per_page`.

**Actual**
Offset uses `+ 1`, so every page skips one

---

## Bug 7: Scan can create duplicate findings

**Severity:** Medium

**Endpoint / Area:** Scanner Service `POST /scans`

**Steps to reproduce**
1. Run a scan for asset A with vulnerability V
2. Run the same scan again
3. List findings for asset A

**Expected**
Dedup by `(asset_id, vulnerability_id)` (or enforce unique constraint)

**Actual**
Duplicates are created

---

## Bug 8: UI doesn’t refresh after status update

**Severity:** Low

**Endpoint / Area:** Dashboard UI (`updateStatus()` in `app.js`)

**Steps to reproduce**
1. Update a finding status from the UI.
2. Look at the table/summary.

**Expected**
Table/summary refresh after success.

**Actual**
Only a success message. Data stays stale until manual refresh.

---

## Bug 9: Dashboard UI can’t load assets (CORS)

**Severity:** High

**Endpoint / Area:** Dashboard UI → Scanner Service (`GET http://localhost:8001/assets`)

**Steps to reproduce**
1. Open Dashboard UI (`http://localhost:8000`).
2. Open browser DevTools → Network/Console.
3. Observe request to `http://localhost:8001/assets?per_page=50` failing.

**Expected**
UI loads assets from Scanner Service and the assets table is populated.

**Actual**
Browser blocks the request with CORS error (missing `Access-Control-Allow-Origin`)
Assets table stays empty...
