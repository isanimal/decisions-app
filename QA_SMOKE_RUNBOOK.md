# QA Smoke Testing Runbook

**Purpose**: Quick verification that app is functional.  
**Time**: ~15–20 minutes  
**Frequency**: Every build / before formal QA

## Runbook Steps

````
☐ 1. Server Startup
   - Command: uvicorn app.main:app --reload --port 8000
   - Expected: "Uvicorn running on http://127.0.0.1:8000"
   - Location: /Users/macbookpro/testing/Vscode/Decisions/decisions-app/secure_decision
   - Logs show: No errors, reloader active

☐ 2. Home Page
   - URL: http://localhost:8000/
   - Check: "Secure Decision" title visible
   - Check: Top nav shows Home/Decisions/Threat Lite/KB/Mentions
   - Check: No 404/500 in browser console
   - Check: "Login" link present (unauthenticated)

☐ 3. Initial Setup
   - URL: http://localhost:8000/setup
   - Action: Create admin user
     - Username: admin_user
     - Password: TestPass123!
   - Expected: Success message; redirected to home
   - Note: Only works once; subsequent accesses should show "Already set up"

☐ 4. Login
   - URL: http://localhost:8000/login
   - Action: Login with credentials from step 3
   - Expected:
     - Redirected to home after login
     - Top nav now shows "Signed in as admin_user"
     - "Logout" button visible
   - Check: No 500 error

☐ 5. Decision List
   - Click: "Decisions" in top nav
   - Expected:
     - Page loads without 404/500
     - List displays 10+ seeded decisions
     - Filter controls present (status, team, etc.)
     - "New Decision" button visible
   - Check: All decisions shown with status badges (DRAFT, ACTIVE, SUPERSEDED)

☐ 6. Create Decision
   - Click: "New Decision" button
   - Fill form:
     - Title: "Test Decision XYZ"
     - Context: "Test context about the decision"
     - Goals: "Achieve security objective"
     - Assumptions: "Assuming infrastructure in place"
   - Action: Click "Save"
   - Expected:
     - Redirect to decision detail page
     - Status badge shows "DRAFT"
     - All fields populated on detail page
     - Flash message: "Decision created successfully"

☐ 7. View Decision Detail
   - Current page: Decision detail (from step 6)
   - Check:
     - Title, context, goals, assumptions all visible
     - Status badge shows "DRAFT"
     - Action menu present (Edit, Export, History buttons)
     - "New Threat Assessment" link visible
     - Timestamp shows recent creation

☐ 8. Create Threat Lite Assessment
   - Click: "New Threat Assessment" on decision
   - Expected: Form loads with 6-step fields
   - Fill:
     - Step 1 (Context): "Describe the threat context"
     - Step 2 (Assumptions): "List threat assumptions"
     - Step 3 (Stress Test): "Describe stress test scenarios"
     - Step 4 (Boundaries): "Define boundaries"
     - Step 5 (Threat Scenarios): "List actual threat scenarios" (required)
     - Step 6 (Reflection): "Reflection notes"
   - Action: Click "Save"
   - Expected:
     - Redirect to threat detail page
     - All 6 steps visible
     - Flash message: "Assessment created successfully"
     - Linked to correct decision

☐ 9. View Threat Lite Assessment
   - Current page: Threat detail (from step 8)
   - Check:
     - All 6 steps displayed in order
     - Decision title/link shown
     - Status/outcome indicator visible
     - Edit & Archive buttons present

☐ 10. Edit Decision
   - Click: "Edit" on decision detail (from step 7)
   - Expected: Form loads with current values pre-filled
   - Action: Change title to "Test Decision XYZ (Edited)"
   - Action: Click "Save"
   - Expected:
     - Redirect to decision detail
     - Title updated
     - Flash message: "Decision updated"
     - Check: Revision history should now show 2 entries

☐ 11. View Revision History
   - Click: "History" link on decision detail
   - Expected:
     - History page loads (no 404)
     - Shows 2 revisions (initial creation + edit)
     - Each revision has timestamp and diff link
     - Can click "Compare" to view side-by-side

☐ 12. Compare Revisions
   - Click: "Compare" link on older revision (from step 11)
   - Expected:
     - Diff page loads
     - Shows changes between revisions
     - Original title highlighted
     - New title highlighted
     - No 500 error

☐ 13. Knowledge Base List
   - Click: "Knowledge Base" in top nav
   - Expected:
     - KB page loads (no 404)
     - Card list visible (30+ cards expected)
     - Cards show: Title, Category, Severity, Tags
     - Search/filter controls present

☐ 14. KB Card Search (API Test)
   - Tool: Use curl, Postman, or browser DevTools
   - Command:
     ```
     curl -X POST http://localhost:8000/kb/match \
       -H "Content-Type: application/json" \
       -d '{"decision_pattern": "microservices", "tags": ["microservices"]}'
     ```
   - Expected:
     - 200 OK response
     - JSON with "results" array
     - Results include score field
     - At least 1 card with "microservices" in content

☐ 15. Export Decision (JSON)
   - Go to: Decision detail page (step 7)
   - Click: "Export" button → "Export JSON"
   - Expected:
     - JSON file downloads
     - File parseable JSON
     - Contains decision title, context, threats
     - Valid schema

☐ 16. Activate Decision (ADMIN only)
   - Precondition: Already logged in as admin_user
   - Go to: DRAFT decision detail
   - Click: "Activate" button (ADMIN-only, if visible)
   - Expected:
     - Status badge changes from "DRAFT" to "ACTIVE"
     - Button now shows "Supersede" instead
     - Flash message: "Decision activated"
     - Check: If user is MEMBER/VIEWER, button should be hidden

☐ 17. Supersede Decision (ADMIN only)
   - Precondition: Decision is ACTIVE (from step 16)
   - Click: "Supersede" button
   - Optional: Specify superseding decision ID
   - Expected:
     - Status changes to "SUPERSEDED"
     - Button hidden
     - Flash message: "Decision superseded"

☐ 18. Archive Decision
   - Precondition: Create new test decision
   - Click: "Archive" button (if visible in action menu)
   - Expected:
     - Decision soft-deleted
     - Disappears from decision list
     - Detail page shows "ARCHIVED" badge
     - Can still access via direct URL

☐ 19. Delete Decision
   - Precondition: Create new test decision
   - Click: "Delete" button
   - Confirm if prompted
   - Expected:
     - Decision hard-deleted
     - Redirected to decision list
     - 404 when trying to access deleted decision ID
     - Flash message: "Decision deleted"

☐ 20. Logout
   - Click: "Logout" button in top nav
   - Expected:
     - Redirected to login page
     - Session cleared
     - Trying to access /decisions → redirected to /login
     - Top nav shows "Login" link again

☐ 21. Protected Routes Check
   - Action: Clear all cookies/session
   - Try to access: http://localhost:8000/decisions
   - Expected: Redirected to /login (not 500)
   - Try to access: http://localhost:8000/kb
   - Expected: Redirected to /login (not 500)

☐ 22. Final Verification
   - Server logs: No 500 errors
   - Console: No JavaScript errors
   - All buttons clickable
   - All forms submit without errors
   - Navigation fully functional
````

## Pass/Fail Criteria

**PASS**: All 22 steps completed without:

- 500 Internal Server Errors
- Unhandled exceptions in logs
- 404 on primary navigation
- Template rendering errors
- CSRF validation failures on POST

**FAIL**: Any step encounters:

- 500 error
- Unexpected redirect to /login (when authenticated)
- Form submission error
- Missing required UI element (button, link, form field)

## Sign-Off

**Date Tested**: ******\_\_\_\_******  
**Tester Name**: ******\_\_\_\_******  
**Build/Version**: v0.1  
**Overall Status**: ☐ PASS | ☐ FAIL

**Issues Found** (if any):

```
1.
2.
3.
```

**Notes**:

```
_________________________________________________________________
_________________________________________________________________
```
