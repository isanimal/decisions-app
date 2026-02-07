# QA Testing Documentation Summary

**Version**: 1.0  
**Date**: 2026-02-07  
**For**: Secure Decision App v0.1

---

## Overview

This QA testing package provides comprehensive documentation for testing the **Secure Decision App**, a FastAPI-based decision management system with threat modeling and knowledge base integration.

### What's Included

1. **QA_TEST_PLAN.md** — Complete test matrix with 108+ test cases organized by feature
2. **QA_SMOKE_RUNBOOK.md** — Quick 22-step verification checklist (~15-20 min)
3. **QA_REPORT_TEMPLATE.md** — Template for documenting test results and issues
4. **ISSUE_LOG.md** — Template for tracking and investigating defects
5. **This Document** — Summary and navigation guide

---

## Quick Start

### For First-Time QA

1. **Review the test environment setup** (QA_TEST_PLAN.md Section 4)
   - Start the server
   - Initialize the database
   - Create test users

2. **Run the smoke test** (QA_SMOKE_RUNBOOK.md)
   - Takes ~20 minutes
   - Covers happy path and key features
   - Quick pass/fail validation

3. **If smoke test passes**: Proceed to detailed testing matrix

4. **If smoke test fails**:
   - Log the issue in ISSUE_LOG.md
   - Investigate root cause
   - Create bug report in ISSUE_LOG with reproduction steps

---

### For Formal QA Campaign

1. **Prepare test environment** (Section 4 of QA_TEST_PLAN.md)
2. **Execute all test cases** from the test matrix (Section 5)
   - Navigation (NAV-\*)
   - Authentication (AUTH-\*)
   - Decision Management (DECISION-\*)
   - Threat Lite (THREAT-\*)
   - Knowledge Base (KB-\*)
   - Export/Import (EXPORT-\*)
   - Negative & Edge Cases (EDGE-\*)
   - Regression Tests (REG-\*)

3. **Document results** as you test
   - Mark each test PASS, FAIL, or SKIP
   - For failures, create issue entry in ISSUE_LOG.md

4. **Generate QA Report**
   - Use QA_REPORT_TEMPLATE.md
   - Fill in pass/fail counts by category
   - List all issues by severity
   - Add sign-off from QA lead

---

## Test Matrix Organization

### by Feature Area

| Feature                        | Test IDs                     | Count   | Focus                                                  |
| ------------------------------ | ---------------------------- | ------- | ------------------------------------------------------ |
| Navigation & UI                | NAV-001 to NAV-008           | 8       | Menu visibility, link integrity, 404 handling          |
| Authentication & Authorization | AUTH-001 to AUTH-013         | 13      | Login, logout, roles, CSRF, session timeout            |
| Decision Management            | DECISION-001 to DECISION-026 | 26      | CRUD, status workflow, archive/delete, history, export |
| Threat Lite Assessment         | THREAT-001 to THREAT-015     | 15      | CRUD, 6-step methodology, linking, KB matching         |
| Knowledge Base                 | KB-001 to KB-015             | 15      | Status, list, search, matching, disabled cards         |
| Export & Import                | EXPORT-001 to EXPORT-009     | 9       | JSON export, HTML export, bulk import, validation      |
| Negative & Edge Cases          | EDGE-001 to EDGE-014         | 14      | XSS, SQL injection, IDOR, long input, special chars    |
| Regression Tests               | REG-001 to REG-008           | 8       | Template blocks, route availability, CSRF, JSON        |
| **TOTAL**                      | –                            | **108** | –                                                      |

---

## Key Test Scenarios

### Core Workflow

**Decision Lifecycle**:

```
1. Create Decision (DRAFT)
   └─ Create Threat Lite Assessment
      └─ Search Knowledge Base for relevant cards
         └─ Generate recommendations
2. View Decision Details
   └─ Review all threats
   └─ Export as JSON/HTML
3. Edit Decision
   └─ Create revision history entry
   └─ Compare old vs new
4. Activate Decision (ADMIN)
   └─ Status: DRAFT → ACTIVE
5. Supersede Decision (ADMIN)
   └─ Status: ACTIVE → SUPERSEDED
```

### Access Control

**User Roles**:

- **VIEWER**: Read-only access, no create/edit
- **MEMBER**: CRUD decisions, threats (own team), can view KB
- **ADMIN**: All permissions, activate/supersede, user management, KB disable

---

## Known Fragile Points

### 1. Template Block Closure (REG-001)

- **Risk**: Mismatched `{% block %}` / `{% endblock %}` causes partial rendering
- **Test**: Render each template; inspect HTML validity
- **Watch**: `decision_view.html`, `threat_lite_view.html` (large files)

### 2. CSRF Token Validation (AUTH-012)

- **Risk**: Token not regenerated per session; same token across users
- **Test**: Submit POST without token (should 403); with valid token (should 200)
- **Watch**: Session middleware; form token generation in template

### 3. IDOR Vulnerabilities (EDGE-003, EDGE-004)

- **Risk**: Access threat `/decisions/2/threat-lite/3` when threat belongs to decision 1
- **Test**: Confirm 404 when threat_id doesn't match decision_id
- **Watch**: All sub-resource routes validate parent-child relationships

### 4. KB Loader Case Sensitivity (KB-010)

- **Risk**: `.yml` files read but `.YAML` files skipped (or vice versa)
- **Test**: Verify 30 cards loaded; check KB status endpoint
- **Watch**: Glob pattern in `kb_loader.py` uses `.lower()` on file extensions

### 5. Concurrent Edits (EDGE-008)

- **Risk**: Last-write-wins without conflict detection
- **Test**: Two users edit same decision; verify no data loss
- **Watch**: No optimistic locking implemented; expected behavior = last write wins

### 6. SQLite JSON Fields (Regression)

- **Risk**: JSON fields (tags, assessment_ids) may not serialize/deserialize correctly
- **Test**: Create KB card, verify tags stored and retrieved correctly
- **Watch**: SQLAlchemy JSON field mapping; SQLite quirks

---

## Test Execution Checklist

### Before Testing

- [ ] Clone/pull latest code
- [ ] Create fresh database: `python scripts/create_tables.py`
- [ ] Seed data: `python scripts/seed_kb_and_decisions.py`
- [ ] Start server: `uvicorn app.main:app --reload --port 8000`
- [ ] Verify no startup errors
- [ ] Open browser to http://localhost:8000

### During Testing

- [ ] Record start time
- [ ] Mark each test PASS/FAIL in test matrix
- [ ] For each FAIL: Create issue entry in ISSUE_LOG.md
- [ ] Note browser/OS if issue is specific
- [ ] Take screenshots of failures
- [ ] Record server logs if 500 error

### After Testing

- [ ] Complete QA_REPORT_TEMPLATE.md
- [ ] Count issues by severity
- [ ] Recommend next actions
- [ ] Get sign-offs (QA, Dev, PO)

---

## Issue Tracking Process

### 1. Find a Bug During Testing

### 2. Create Issue Entry (ISSUE_LOG.md)

- Assign Issue ID (ISS-001, ISS-002, etc.)
- Fill in all required fields
- Include reproduction steps
- Attach screenshots/logs

### 3. Categorize by Severity

- **CRITICAL**: Blocks release (auth bypass, 500 errors, data loss)
- **HIGH**: Major feature broken (export fails, CRUD missing)
- **MEDIUM**: Minor feature broken (UI glitch, off-by-one)
- **LOW**: Cosmetic (typo, spacing)

### 4. Track Status

- **Open**: Reported, awaiting investigation
- **In Progress**: Dev team working on it
- **Fixed**: Code changed, awaiting QA verification
- **Closed**: Verified fixed
- **Wontfix**: Decided not to fix (document reason)

### 5. Follow Up

- Test fix when dev says "Fixed"
- Re-run test case that failed
- Check for regressions (run smoke test again)

---

## Browser/Environment Matrix

### Required Testing

| Browser | Version | Required    | Notes                             |
| ------- | ------- | ----------- | --------------------------------- |
| Chrome  | Latest  | ✅ Yes      | Primary browser                   |
| Firefox | Latest  | ✅ Yes      | Cross-browser verification        |
| Safari  | Latest  | ⚠️ Optional | macOS only (Nice to have)         |
| Edge    | Latest  | ⚠️ Optional | Windows validation (Nice to have) |

### Python & Database

| Component  | Version | Notes              |
| ---------- | ------- | ------------------ |
| Python     | 3.14.2  | Must match `.venv` |
| FastAPI    | 0.104+  | Core framework     |
| SQLAlchemy | 2.0+    | ORM                |
| SQLite     | 3.x     | In-file database   |
| Uvicorn    | Latest  | ASGI server        |

---

## Success Criteria

### Smoke Test (22 steps)

**PASS**: All 22 steps completed without:

- 500 Internal Server Errors
- Unhandled exceptions in logs
- 404 on primary navigation
- Template rendering errors
- CSRF validation failures

### Formal QA Campaign

**PASS**:

- ≥90% test cases pass
- All CRITICAL issues resolved
- All HIGH issues resolved or documented
- No regressions from previous build
- Security checklist complete

**FAIL**:

- <90% pass rate
- Unresolved CRITICAL/HIGH issues
- New regression detected
- Security vulnerabilities found

---

## Report Delivery

### Final QA Report Should Include

1. **Executive Summary** (2-3 sentences)
   - Overall pass/fail status
   - Key findings
   - Risk assessment

2. **Test Coverage** (table)
   - Tests run by category
   - Pass/fail/skip counts
   - Success percentage

3. **Issues Found** (by severity)
   - CRITICAL: [count] issues
   - HIGH: [count] issues
   - MEDIUM: [count] issues
   - LOW: [count] issues

4. **Sign-Offs**
   - QA Lead: ✓ Approved / ✗ Needs Work
   - Dev Lead: ✓ Acknowledged / ? Questions
   - Product Owner: ✓ Ready to Release / ✗ Hold

5. **Recommendations**
   - Fix critical/high before release
   - Medium issues in next sprint
   - Low issues in backlog

---

## Automated Testing (Optional Future)

### Python pytest Smoke Suite

Minimal CI/CD test suite (5 critical tests):

```bash
pytest tests/test_smoke.py -v
```

Tests to automate:

1. Home page loads
2. Login flow works
3. Create decision + threat
4. KB search returns results
5. Protected routes require auth

---

## Contact & Questions

**QA Lead**: [Name]  
**Dev Lead**: [Name]  
**Product Owner**: [Name]

**Questions About**:

- **Test execution**: See QA_TEST_PLAN.md Section 4-5
- **Smoke runbook**: See QA_SMOKE_RUNBOOK.md
- **Issue tracking**: See ISSUE_LOG.md
- **Report format**: See QA_REPORT_TEMPLATE.md

---

## Document References

| Document               | Purpose                          | When to Use            |
| ---------------------- | -------------------------------- | ---------------------- |
| QA_TEST_PLAN.md        | Complete test matrix (108 cases) | Formal QA campaign     |
| QA_SMOKE_RUNBOOK.md    | Quick 22-step checklist          | Daily/build validation |
| QA_REPORT_TEMPLATE.md  | Test results documentation       | End of QA campaign     |
| ISSUE_LOG.md           | Defect tracking template         | Throughout testing     |
| This Document (README) | Navigation & overview            | Getting started        |

---

## Changelog

| Version | Date       | Changes                          |
| ------- | ---------- | -------------------------------- |
| 1.0     | 2026-02-07 | Initial QA documentation package |

---

**End of QA Testing Documentation Summary**
