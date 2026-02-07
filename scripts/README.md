# QA Test Automation Suite

Complete automated testing framework for Secure Decision App with 50+ test scripts across multiple categories.

## 📋 Test Scripts Overview

### 1. **qa_smoke_test.py** - Smoke Testing (21 tests)

Quick validation that core application features work.

**Tests:**

- Home page loads
- User setup and login
- Decision CRUD (Create, Read, Update)
- Threat assessment CRUD
- Knowledge base access
- Export functionality
- Status transitions (activate, supersede, archive)
- Authentication & logout
- Protected routes
- Error handling

**Usage:**

```bash
# Run with default settings
python scripts/qa_smoke_test.py

# Run with custom URL and verbose output
python scripts/qa_smoke_test.py --url http://localhost:8000 --verbose

# Expected output: ~20-30 seconds, all tests PASS
```

**Output:**

```
[HH:MM:SS] START  Starting QA Smoke Test Suite
[HH:MM:SS] TEST   Step 1: ✓ PASS - Home page loads
...
[HH:MM:SS] TEST   Step 21: ✓ PASS - No 500 errors during test
======================================================================
                      QA SMOKE TEST SUMMARY
======================================================================
Total Tests: 21
Passed:      21 ✓
Failed:      0 ✗
Success Rate: 100.0%
Duration:    XX.X seconds
======================================================================
✓ ALL TESTS PASSED
```

---

### 2. **qa_test_suite.py** - Comprehensive Testing (30+ tests)

Full feature coverage organized by category.

**Test Categories:**

- **Navigation (NAV-001 to NAV-004)** - Menu items, highlighting, 404 handling, link integrity
- **Authentication (AUTH-001 to AUTH-004)** - Setup, login, route protection, logout
- **Decision CRUD (DECISION-001 to DECISION-007)** - Create, read, edit, list, archive, history, export
- **Threat Assessment (THREAT-001 to THREAT-003)** - Create, view, IDOR prevention
- **Knowledge Base (KB-001 to KB-003)** - Status, list, search functionality
- **Export/Import (EXPORT-001)** - Bulk data export
- **Edge Cases (EDGE-001 to EDGE-002)** - XSS prevention, long input handling
- **Regression (REG-001 to REG-002)** - Template integrity, CSRF protection

**Usage:**

```bash
# Run comprehensive test suite
python scripts/qa_test_suite.py

# With verbose output
python scripts/qa_test_suite.py --verbose

# Expected output: ~30-60 seconds, all tests PASS
```

**Output:**

```
================================================================================
COMPREHENSIVE QA TEST SUITE REPORT
================================================================================
Total Tests:     30
Passed:          30 ✓
Failed:          0 ✗
Success Rate:    100.0%
Duration:        XX.X seconds
================================================================================

Results by Category:
--------------------------------------------------------------------------------
Navigation           4/4 passed (100.0%)
Authentication       4/4 passed (100.0%)
Decision CRUD        7/7 passed (100.0%)
Threat Lite          3/3 passed (100.0%)
Knowledge Base       3/3 passed (100.0%)
Export/Import        1/1 passed (100.0%)
Edge Cases           2/2 passed (100.0%)
Regression           2/2 passed (100.0%)
================================================================================
```

---

### 3. **qa_security_tests.py** - Security Testing (16+ tests)

Vulnerability assessment and security validation.

**Test Categories:**

- **Authentication (AUTH-SEC-001 to AUTH-SEC-003)**
  - Weak password rejection
  - SQL injection in login
  - Session fixation prevention

- **CSRF (CSRF-001 to CSRF-002)**
  - CSRF token presence
  - POST validation without token

- **IDOR (IDOR-001 to IDOR-003)**
  - Decision access control
  - Threat access isolation
  - Invalid ID handling

- **XSS (XSS-001 to XSS-003)**
  - Script tag escaping
  - Event handler escaping
  - JSON response safety

- **Information Disclosure (INFO-001 to INFO-003)**
  - Error message sanitization
  - Debug mode disabled
  - Server version hiding

- **Auth Bypass (AUTHBYPASS-001)**
  - Null byte injection prevention

- **Input Validation (INPUT-001 to INPUT-002)**
  - Excessive input rejection
  - Special character handling

**Severity Levels:**

- 🔴 **CRITICAL** - Must fix immediately
- 🟠 **HIGH** - Should fix before release
- 🟡 **MEDIUM** - Consider fixing
- 🟢 **LOW** - Minor improvement

**Usage:**

```bash
# Run security tests
python scripts/qa_security_tests.py

# With verbose output
python scripts/qa_security_tests.py --verbose

# Expected output: All tests SAFE (no vulnerabilities)
```

**Output:**

```
================================================================================
SECURITY TEST SUITE
================================================================================
[CRITICAL] AUTH-SEC-002: ✓ SAFE - SQL injection blocked
[HIGH]     CSRF-001: ✓ SAFE - CSRF token in forms
[HIGH]     IDOR-001: ✓ SAFE - Decision access controlled
[HIGH]     XSS-001: ✓ SAFE - Script tags escaped
...

================================================================================
SECURITY TEST REPORT
================================================================================
Total Tests:         16
Passed (Safe):       16 ✓
Failed (Vulnerable): 0 ✗
Success Rate:        100.0%
================================================================================

Vulnerabilities Found:
  CRITICAL: 0
  HIGH:     0
  MEDIUM:   0
  LOW:      0

================================================================================
✓ NO CRITICAL/HIGH VULNERABILITIES FOUND
================================================================================
```

---

### 4. **run_all_tests.py** - Master Test Runner

Orchestrates all test suites with consolidated reporting.

**Usage:**

```bash
# Run all test suites
python scripts/run_all_tests.py

# Run specific suite
python scripts/run_all_tests.py --suite smoke
python scripts/run_all_tests.py --suite comprehensive
python scripts/run_all_tests.py --suite security

# With custom URL and verbose
python scripts/run_all_tests.py --url http://localhost:8000 --verbose

# Expected output: 2-3 minutes for all suites
```

**Output:**

```
================================================================================
SECURE DECISION APP - MASTER TEST SUITE
Target: http://localhost:8000
Started: 2024-XX-XX HH:MM:SS
================================================================================

================================================================================
Running Smoke Tests...
================================================================================
...

================================================================================
Running Comprehensive Tests...
================================================================================
...

================================================================================
Running Security Tests...
================================================================================
...

================================================================================
MASTER TEST SUMMARY
================================================================================
Total Suites:      3
Passed:            3 ✓
Failed:            0 ✗
Success Rate:      100.0%
Total Duration:    XX.X seconds
================================================================================

Suite Results:
--------------------------------------------------------------------------------
Smoke Tests                    ✓ PASS
Comprehensive Tests            ✓ PASS
Security Tests                 ✓ PASS

================================================================================
✓ ALL TEST SUITES PASSED
Application is ready for deployment
================================================================================
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies
pip install requests

# Ensure server is running
curl http://localhost:8000/
```

### 2. Run Tests

**Quick smoke test (20 seconds):**

```bash
cd decisions-app/scripts
python qa_smoke_test.py
```

**Full comprehensive testing (2-3 minutes):**

```bash
python run_all_tests.py
```

**Security audit only:**

```bash
python qa_security_tests.py
```

### 3. Interpret Results

| Exit Code | Meaning             |
| --------- | ------------------- |
| 0         | All tests passed ✓  |
| 1         | Some tests failed ✗ |

---

## 📊 Test Coverage Matrix

| Feature          | Smoke  | Comprehensive    | Security         | Coverage      |
| ---------------- | ------ | ---------------- | ---------------- | ------------- |
| Navigation       | —      | NAV-001~004      | —                | 4 tests       |
| Authentication   | ✓      | AUTH-001~004     | AUTH-SEC-001~003 | 7 tests       |
| Decision CRUD    | ✓      | DECISION-001~007 | —                | 8 tests       |
| Threat CRUD      | ✓      | THREAT-001~003   | —                | 4 tests       |
| Knowledge Base   | ✓      | KB-001~003       | —                | 4 tests       |
| Export/Import    | ✓      | EXPORT-001       | —                | 2 tests       |
| CSRF             | —      | REG-002          | CSRF-001~002     | 3 tests       |
| IDOR             | —      | THREAT-003       | IDOR-001~003     | 4 tests       |
| XSS              | —      | EDGE-001         | XSS-001~003      | 4 tests       |
| Input Validation | —      | EDGE-002         | INPUT-001~002    | 3 tests       |
| Error Handling   | ✓      | REG-001          | INFO-001~003     | 4 tests       |
| **TOTAL**        | **21** | **30**           | **16**           | **~67 tests** |

---

## 🔧 Common Issues & Solutions

### Issue: "Connection refused"

**Cause:** Server not running on localhost:8000

```bash
# Start the server
cd decisions-app
python -m app.main
```

### Issue: "404 on /setup"

**Cause:** Already set up, use existing credentials

```bash
# Try login instead
# Default: admin / Admin123!
```

### Issue: "Timeout errors"

**Cause:** Server too slow or network issues

```bash
# Run with custom timeout
python qa_smoke_test.py --url http://localhost:8001
```

### Issue: "CSRF token not found"

**Cause:** CSRF middleware not active

```bash
# Check server logs for middleware configuration
```

---

## 📈 Performance Benchmarks

| Suite          | Tests  | Avg Duration | Per-Test |
| -------------- | ------ | ------------ | -------- |
| Smoke          | 21     | 20-30s       | 1-2s     |
| Comprehensive  | 30     | 30-60s       | 1-2s     |
| Security       | 16     | 15-25s       | 1-2s     |
| **All Suites** | **67** | **90-120s**  | **1-2s** |

**Network latency strongly affects results. Slower networks may show 2-3x slower times.**

---

## 🔍 Detailed Test Descriptions

### Smoke Tests (qa_smoke_test.py)

**Test 1-3:** Home → Setup → Login

- Validates application starts and authentication works

**Test 4-6:** Decision CRUD

- Creates a test decision, views it, edits it

**Test 7-8:** Threat Assessment

- Creates and views threat assessment

**Test 9-11:** Decision Operations

- Views history, revision comparison

**Test 12-13:** Knowledge Base

- Lists and searches KB cards with JSON API

**Test 14-16:** Status Transitions

- Tests activate, supersede, archive operations

**Test 17-20:** Cleanup & Security

- Tests delete, logout, auth protection

**Test 21:** Error Check

- Verifies no 500 errors during entire test run

---

### Comprehensive Tests (qa_test_suite.py)

Similar to smoke tests but with additional edge cases:

- All 21 smoke test scenarios
- Menu navigation testing
- Long input (5000 chars)
- XSS payload handling
- CSV export validation
- Pagination testing
- IDOR prevention
- Template integrity

---

### Security Tests (qa_security_tests.py)

**Authentication Security:**

- SQL injection: `' OR '1'='1`
- Weak password detection
- Session fixation after login

**CSRF Protection:**

- Token presence in forms
- POST request validation

**IDOR Prevention:**

- Cross-user access blocking
- Invalid parameter handling

**XSS Prevention:**

- `<script>alert('xss')</script>`
- SVG event handlers
- JSON response escaping

**Information Disclosure:**

- Error message sanitization
- Debug mode disabled
- Server version hidden

---

## 📝 CI/CD Integration

### GitHub Actions Example

```yaml
name: QA Tests

on: [push, pull_request]

jobs:
  qa-tests:
    runs-on: ubuntu-latest
    services:
      app:
        image: secure-decision:latest
        ports:
          - 8000:8000

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install requests

      - name: Run QA tests
        run: python scripts/run_all_tests.py --url http://localhost:8000

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: qa-results
          path: qa-results/
```

---

## 📞 Support & Documentation

**For detailed test information:**

- See `QA_TEST_PLAN.md` for test matrix and specifications
- See `QA_README.md` for manual testing guide
- See `ISSUE_LOG.md` for bug tracking
- See `QA_REPORT_TEMPLATE.md` for results format

**Script Documentation:**

- Each script has inline comments and docstrings
- Run with `--verbose` flag for detailed output
- Check exit codes for CI/CD integration

---

## ✅ Quality Gates

Tests should pass before:

- ✓ Pushing to main branch
- ✓ Creating pull requests
- ✓ Deploying to staging
- ✓ Releasing to production

**Success Criteria:**

- Smoke tests: 100% pass rate
- Comprehensive tests: 95%+ pass rate
- Security tests: No CRITICAL vulnerabilities
- Total duration: < 3 minutes

---

## 📄 Test Execution Log Template

```
Date: YYYY-MM-DD HH:MM:SS
Tester: [Name]
Environment: [URL]
Python: [Version]

Smoke Tests:      [P/F] XX/21 passed
Comprehensive:    [P/F] XX/30 passed
Security Tests:   [P/F] XX/16 passed

Issues Found:
- [Issue ID]: [Description]

Recommendations:
- [Action item]

Sign-off: _______________
```

---

## 🎯 Future Enhancements

Planned additions:

- [ ] Performance/load testing suite
- [ ] API contract testing
- [ ] Database integrity checks
- [ ] Multi-user concurrency tests
- [ ] HTML report generation
- [ ] Test coverage metrics
- [ ] Parallel test execution
- [ ] Mock server mode
- [ ] Test data fixtures
- [ ] Regression test tagging

---

Last Updated: 2024-12-XX
Version: 1.0 - Complete Testing Framework
