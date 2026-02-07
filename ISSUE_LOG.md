# Issue Log: Secure Decision App v0.1

**Document Purpose**: Track all defects found during QA testing.  
**Format**: Central issue registry with detailed investigation for each item.  
**Update Frequency**: After each test session

---

## Issue Summary Table

| Issue ID | Title | Severity | Area | Status                        | Assigned To | Found Date |
| -------- | ----- | -------- | ---- | ----------------------------- | ----------- | ---------- |
|          |       |          |      | Open/In Progress/Fixed/Closed |             |            |
|          |       |          |      | Open/In Progress/Fixed/Closed |             |            |
|          |       |          |      | Open/In Progress/Fixed/Closed |             |            |

---

## Detailed Issue Logs

### Issue #1 (Template)

**Issue ID**: ISS-001  
**Title**: [Describe the issue in one sentence]  
**Severity**: ☐ CRITICAL | ☐ HIGH | ☐ MEDIUM | ☐ LOW  
**Area**: ☐ Decision | ☐ ThreatLite | ☐ KB | ☐ Export | ☐ UI | ☐ Auth | ☐ Security | ☐ Other  
**Status**: ☐ Open | ☐ In Progress | ☐ Fixed | ☐ Closed | ☐ Wontfix  
**Assigned To**: ******\_\_\_\_******  
**Found Date**: ******\_\_\_\_******  
**Fixed Date**: ******\_\_\_\_****** (if applicable)

---

#### Steps to Reproduce

```
1. [First step to reproduce]
2. [Second step]
3. [Third step]
```

---

#### Expected Result

[Describe what should happen]

---

#### Actual Result

[Describe what actually happens]

---

#### Evidence

- Screenshot: [Path/Link/Description]
- Log: [Paste relevant error from server log]
- Video: [Link if applicable]

```
[Paste relevant error output]
```

---

#### Environment Details

- **OS**: macOS
- **Browser**: Chrome 130 / Firefox / Safari
- **Python Version**: 3.14.2
- **Build**: v0.1
- **Database**: SQLite (secure_decision.db)
- **User Role**: ADMIN / MEMBER / VIEWER / Unauthenticated

---

#### Suspected Root Cause

**File(s)**:

- `app/main.py` (line \_\_)
- `app/models.py` (line \_\_)
- `app/templates/xxx.html` (line \_\_)

**Hypothesis**:
[Explain why you think this is happening. Reference code if possible.]

```python
# Example: If in main.py
@app.get("/decisions/{id}")
def get_decision(id: int):
    # Bug: Missing query filter for decision.user_id
    decision = db.query(Decision).filter(Decision.id == id).first()
    # Should be: filter(Decision.id == id, Decision.user_id == current_user.id)
```

---

#### Fix Recommendation

[Specific code changes or configuration updates needed]

**Suggested Fix**:

```python
# Replace this:
decision = db.query(Decision).filter(Decision.id == id).first()

# With this:
decision = db.query(Decision).filter(
    Decision.id == id,
    Decision.user_id == current_user.id
).first()
```

**Testing Steps to Verify Fix**:

1. Make code change
2. Restart server
3. [Reproduce issue again and verify it's fixed]
4. [Verify regression tests still pass]

---

#### Impact Assessment

**User Impact**: [Who/how many users affected?]

- CRITICAL: All users, app unusable
- HIGH: Many users, core feature broken
- MEDIUM: Some users, partial feature broken
- LOW: Few users, cosmetic issue

**Data Risk**: ☐ Yes | ☐ No  
[If yes, explain data integrity/loss risk]

**Regression Risk**: ☐ High | ☐ Medium | ☐ Low  
[Does fix introduce risk of breaking other features?]

---

#### Related Issues

- ISS-002 (if part of same root cause)
- ISS-003

---

#### Notes & Comments

```
[Additional investigation notes, workarounds, etc.]

Example:
- User can work around by refreshing page
- Issue only happens in Firefox, not Chrome
- Intermittent - happens 50% of the time
```

---

## Example Issues (Reference)

### Issue #101 (Example: Auth Failure)

**Issue ID**: ISS-101  
**Title**: CSRF Token not validated on POST /decisions/new  
**Severity**: CRITICAL  
**Area**: Auth  
**Status**: Open  
**Assigned To**: Dev Team  
**Found Date**: 2026-02-07

---

#### Steps to Reproduce

```
1. Open /decisions/new in browser (authenticated)
2. Using DevTools or API client, craft POST to /decisions/new
3. Remove csrf_token field from request body
4. Submit POST request
```

---

#### Expected Result

POST rejected with 403 Forbidden error.

---

#### Actual Result

POST accepted (200 OK) and decision created without CSRF token.

---

#### Evidence

**Request**:

```
POST /decisions/new HTTP/1.1
Host: localhost:8000
Content-Type: application/x-www-form-urlencoded

title=Test&context=Test&goals=Test
(no csrf_token field)
```

**Response**:

```
200 OK
Location: /decisions/5
```

---

#### Suspected Root Cause

**File**: `app/main.py` line 156

Middleware check for CSRF may be missing or disabled. The form POST route doesn't explicitly validate `csrf_token` parameter.

```python
@app.post("/decisions/new")
def create_decision(request: Request, form: FormData):
    # Missing: csrf_token = form.get("csrf_token")
    #         if not verify_csrf_token(csrf_token): return 403
    decision = Decision(title=form["title"], ...)
    db.add(decision)
    db.commit()
```

---

#### Fix Recommendation

Enable CSRF middleware and add explicit validation:

```python
@app.post("/decisions/new")
def create_decision(request: Request, form: FormData):
    csrf_token = form.get("csrf_token")
    session_token = request.session.get("csrf_token")

    if not csrf_token or csrf_token != session_token:
        raise HTTPException(status_code=403, detail="CSRF validation failed")

    decision = Decision(title=form["title"], ...)
    db.add(decision)
    db.commit()
```

**Testing to Verify**:

1. Generate form with CSRF token
2. Submit with token → should succeed (200)
3. Submit without token → should fail (403)
4. Submit with wrong token → should fail (403)

---

#### Impact Assessment

**User Impact**: CRITICAL — CSRF vulnerability allows attackers to hijack sessions and create/modify decisions  
**Data Risk**: YES — Unauthorized decision creation  
**Regression Risk**: LOW — CSRF fix shouldn't affect legitimate users

---

---

### Issue #102 (Example: UI Bug)

**Issue ID**: ISS-102  
**Title**: Threat Lite detail page shows wrong decision title  
**Severity**: HIGH  
**Area**: UI / ThreatLite  
**Status**: In Progress  
**Assigned To**: Frontend Dev  
**Found Date**: 2026-02-06

---

#### Steps to Reproduce

```
1. Create Decision A ("API Security")
2. Create Decision B ("Database Security")
3. Create Threat Lite T1 under Decision A
4. Create Threat Lite T2 under Decision B
5. Navigate to /decisions/A/threat-lite/T2
```

---

#### Expected Result

Threat Lite T2 detail page shows "Database Security" as the decision title.

---

#### Actual Result

Threat Lite T2 detail page shows "API Security" (wrong decision).

---

#### Evidence

**Screenshot**: [Link to screenshot showing T2 with wrong decision title]

---

#### Suspected Root Cause

**File**: `app/templates/threat_lite_view.html` line 12

Template may be fetching decision from wrong context or query not filtering by decision_id.

```jinja2
{# WRONG: #}
{{ threat.decision.title }}  {# May be loading first decision, not correct one #}

{# Correct would check: #}
{% if threat.decision_id == decision_id %}
  {{ threat.decision.title }}
{% endif %}
```

---

#### Fix Recommendation

Verify the route loads both threat AND decision properly:

```python
@app.get("/decisions/{decision_id}/threat-lite/{threat_id}")
def view_threat(decision_id: int, threat_id: int, db: Session):
    threat = db.query(ThreatLiteAssessment).filter(
        ThreatLiteAssessment.id == threat_id,
        ThreatLiteAssessment.decision_id == decision_id  # KEY: Validate decision_id
    ).first()

    if not threat:
        raise HTTPException(status_code=404)

    return render_template("threat_lite_view.html", threat=threat)
```

**Testing**:

1. Create 2 decisions with 1 threat each
2. Access threat under decision 1: Should show correct decision title
3. Access threat under decision 2: Should show correct decision title
4. Try to access threat 1 under decision 2 (wrong decision_id): Should 404

---

#### Impact Assessment

**User Impact**: HIGH — User confusion about which decision a threat belongs to  
**Data Risk**: NO — No data loss, just display issue  
**Regression Risk**: LOW — Doesn't affect other features

---

---

## Legend

**Severity Levels**:

- **CRITICAL**: Blocks release, security vulnerability, data loss, auth bypass
- **HIGH**: Major feature broken, significant UX issue, data integrity risk
- **MEDIUM**: Minor feature broken, workaround available, cosmetic UX issue
- **LOW**: Typo, minor cosmetic issue, doesn't affect functionality

**Status**:

- **Open**: Reported, awaiting investigation
- **In Progress**: Being worked on
- **Fixed**: Code changed, awaiting testing/verification
- **Closed**: Verified fixed
- **Wontfix**: Determined not worth fixing (document reason)

**Areas**:

- Decision: Decision CRUD, status transitions, history, archiving
- ThreatLite: Threat assessment CRUD, 6-step methodology
- KB: Knowledge base loading, searching, matching, disabling cards
- Export: JSON export, HTML export, bulk export/import
- UI: Template rendering, layout, navigation, buttons, forms
- Auth: Login, logout, session, CSRF, roles, permissions
- Security: IDOR, XSS, SQL injection, privilege escalation
- Other: Database, performance, configuration, documentation

---

**End of Issue Log**
