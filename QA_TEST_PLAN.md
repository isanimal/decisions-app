# QA Testing Plan: Secure Decision App (v0.1)

**Document Version**: 1.0  
**Last Updated**: 2026-02-07  
**Test Lead**: QA Team  
**Build Version**: v0.1 (commit: TBD)

---

## 1. Executive Summary

This QA Testing Plan provides comprehensive coverage of the **Secure Decision App**, a FastAPI + Jinja2 application for managing security decisions, threat modeling (Lite), knowledge base matching, and exports.

**Core User Workflows Tested**:

1. Create/View/Edit Decision → View Threat Assessments
2. Create/View/Edit Threat Lite Assessment → Link to Decision
3. Search Knowledge Base by pattern/tags
4. Export decisions in JSON/HTML format
5. User authentication & role-based access control
6. Revision history & decision state transitions (DRAFT → ACTIVE → SUPERSEDED)

**Testing Approach**: Manual functional testing + negative/edge case scenarios.  
**Regression Focus**: Template rendering, route availability, IDOR prevention, CSRF protection.

---

## 2. Route Inventory

| Method | Path                                        | Purpose                         | Template                | Auth Required |
| ------ | ------------------------------------------- | ------------------------------- | ----------------------- | ------------- |
| GET    | `/`                                         | Home page                       | `index.html`            | No            |
| GET    | `/login`                                    | Login form                      | `login.html`            | No            |
| POST   | `/login`                                    | Authenticate user               | –                       | No            |
| POST   | `/logout`                                   | Clear session                   | –                       | Yes           |
| GET    | `/setup`                                    | Initial setup (create admin)    | `setup.html`            | No            |
| POST   | `/setup`                                    | Create initial admin user       | –                       | No            |
| GET    | `/decisions`                                | List all decisions (paginated)  | `decisions_list.html`   | Yes           |
| POST   | `/decisions/new`                            | Create decision                 | –                       | Yes           |
| GET    | `/decisions/new`                            | Decision form                   | `decision_new.html`     | Yes           |
| GET    | `/decisions/{id}`                           | View decision details           | `decision_view.html`    | Yes           |
| POST   | `/decisions/{id}/edit`                      | Update decision                 | –                       | Yes           |
| GET    | `/decisions/{id}/edit`                      | Edit form                       | `decision_edit.html`    | Yes           |
| POST   | `/decisions/{id}/archive`                   | Soft-delete decision            | –                       | Yes           |
| POST   | `/decisions/{id}/delete`                    | Hard-delete decision            | –                       | Yes           |
| POST   | `/decisions/{id}/activate`                  | DRAFT → ACTIVE                  | –                       | Yes (ADMIN)   |
| POST   | `/decisions/{id}/supersede`                 | ACTIVE → SUPERSEDED             | –                       | Yes (ADMIN)   |
| GET    | `/decisions/{id}/history`                   | View revision history           | `decision_history.html` | Yes           |
| GET    | `/decisions/{id}/compare`                   | Compare 2 revisions             | `decision_compare.html` | Yes           |
| GET    | `/decisions/{id}/export.json`               | JSON export                     | – (JSON)                | Yes           |
| GET    | `/decisions/{id}/export`                    | HTML export card                | `decision_export.html`  | Yes           |
| POST   | `/decisions/{id}/comments`                  | Add comment with mentions       | –                       | Yes           |
| GET    | `/export/decisions.json`                    | Bulk export (all decisions)     | – (JSON)                | Yes           |
| POST   | `/import/decisions.json`                    | Bulk import from JSON           | –                       | Yes           |
| GET    | `/threat-lite`                              | List all threat assessments     | `threat_lite_list.html` | Yes           |
| GET    | `/decisions/{id}/threat-lite`               | Threat assessments for decision | `threat_lite_list.html` | Yes           |
| GET    | `/decisions/{id}/threat-lite/new`           | Threat form                     | `threat_lite_new.html`  | Yes           |
| POST   | `/decisions/{id}/threat-lite/new`           | Create threat assessment        | –                       | Yes           |
| GET    | `/decisions/{id}/threat-lite/{tid}`         | View threat assessment          | `threat_lite_view.html` | Yes           |
| GET    | `/decisions/{id}/threat-lite/{tid}/edit`    | Edit threat form                | `threat_lite_edit.html` | Yes           |
| POST   | `/decisions/{id}/threat-lite/{tid}/edit`    | Update threat assessment        | –                       | Yes           |
| POST   | `/decisions/{id}/threat-lite/{tid}/archive` | Soft-delete threat              | –                       | Yes           |
| POST   | `/decisions/{id}/threat-lite/{tid}/delete`  | Hard-delete threat              | –                       | Yes           |
| GET    | `/kb`                                       | KB overview & list              | `kb.html`               | Yes           |
| GET    | `/kb/status`                                | KB loader status (JSON)         | – (JSON)                | No            |
| POST   | `/kb/match`                                 | KB card search API              | – (JSON)                | No            |
| POST   | `/decisions/{id}/kb/match`                  | KB match for decision           | – (JSON)                | Yes           |
| POST   | `/kb/disable/{card_id}`                     | Disable KB card                 | –                       | Yes (ADMIN)   |
| GET    | `/mentions`                                 | Show mentions for user          | `mentions.html`         | Yes           |
| GET    | `/admin/users`                              | Admin: user list                | `admin_users.html`      | Yes (ADMIN)   |
| GET    | `/admin/users/new`                          | Admin: new user form            | `admin_user_new.html`   | Yes (ADMIN)   |
| POST   | `/admin/users/new`                          | Admin: create user              | –                       | Yes (ADMIN)   |

**Total Routes**: 45+ active endpoints

---

## 3. Template Inventory

| Template File                 | Purpose                                    | Extends     | Key Blocks           |
| ----------------------------- | ------------------------------------------ | ----------- | -------------------- |
| `base.html`                   | Site layout, nav, auth state               | –           | `content`, `scripts` |
| `index.html`                  | Home/dashboard                             | `base.html` | `content`            |
| `login.html`                  | Login form                                 | `base.html` | `content`            |
| `setup.html`                  | Admin setup form                           | `base.html` | `content`            |
| `decisions_list.html`         | Decision list, filters, pagination         | `base.html` | `content`            |
| `decision_new.html`           | Create decision form                       | `base.html` | `content`            |
| `decision_view.html`          | Decision details, threat list, action menu | `base.html` | `content`            |
| `decision_edit.html`          | Edit decision form                         | `base.html` | `content`            |
| `decision_history.html`       | Revision history, diff links               | `base.html` | `content`            |
| `decision_compare.html`       | Side-by-side revision comparison           | `base.html` | `content`            |
| `decision_export.html`        | HTML export view, readable format          | `base.html` | `content`            |
| `threat_lite_list.html`       | Threat assessments list, pagination        | `base.html` | `content`            |
| `threat_lite_new.html`        | Create threat form (guided/manual)         | `base.html` | `content`            |
| `threat_lite_view.html`       | Threat details (6-step process)            | `base.html` | `content`            |
| `threat_lite_edit.html`       | Edit threat form                           | `base.html` | `content`            |
| `kb.html`                     | KB overview, card list, disabled state     | `base.html` | `content`            |
| `mentions.html`               | User mentions list                         | `base.html` | `content`            |
| `admin_users.html`            | User management list                       | `base.html` | `content`            |
| `admin_user_new.html`         | Create user form                           | `base.html` | `content`            |
| `components/action_menu.html` | Shared action menu (decision/threat)       | –           | –                    |

**Template Block Closure Risk**: All templates properly extend `base.html` and close blocks.  
**XSS Risk**: Jinja2 auto-escaping enabled; user content in `pre` tags for threat/decision content.

---

## 4. Test Environment Setup

### 4.1 Prerequisites

- Python 3.14.2
- FastAPI 0.104+
- SQLAlchemy 2.0+
- SQLite3
- Uvicorn server
- Virtual environment: `/Users/macbookpro/testing/Vscode/Decisions/.venv`

### 4.2 Database Setup

```bash
cd /Users/macbookpro/testing/Vscode/Decisions/decisions-app/secure_decision

# Clear existing database (optional)
rm -f secure_decision.db

# Run scripts to initialize schema and seed data
python scripts/create_tables.py
python scripts/seed_kb_and_decisions.py
```

### 4.3 Server Startup

```bash
/Users/macbookpro/testing/Vscode/Decisions/.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Expected Output**:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID]
```

### 4.4 Test Data

**Pre-seeded Data** (from scripts):

- 10 Decisions (mix of DRAFT, ACTIVE, SUPERSEDED statuses)
- 12 Threat Lite Assessments
- 30 Knowledge Base Cards (6 categories)
- 0 Users (create via setup page or admin UI)

**Test User Accounts** (to be created during test):

- **admin_user**: role=ADMIN, password=SecureTestPass123!
- **member_user**: role=MEMBER, password=MemberPass456!
- **viewer_user**: role=VIEWER, password=ViewerPass789!
  | TL-07 | ThreatLite | Delete threat-lite | Delete with confirm | Deleted, removed from list | | | |
  | TL-08 | ThreatLite | IDOR prevention | Use mismatched decision_id | 404 or Access denied | | | |
  | KB-01 | KB | Status endpoint | GET `/kb/status` | Loaded: true or false | | | |
  | KB-02 | KB | KB page renders | GET `/kb` | Page loads, match UI visible | | | |
  | KB-03 | KB | Match from decision | Use Match button | Cards render | | | |
  | KB-04 | KB | Disable card | Disable button (admin) | Card hidden on next match | | | |
  | KB-05 | KB | Disabled registry | `disabled.json` updated | Contains disabled ID | | | |
  | EXP-01 | Export | Export JSON v2 | GET `/decisions/{id}/export.json` | JSON contains decision/threat_lite/revisions | | | |
  | EXP-02 | Export | Export cards HTML | GET `/decisions/{id}/export` | Card layout renders | | | |
  | NEG-01 | Negative | Required fields | Submit empty required forms | Validation errors, no crash | | | |
  | NEG-02 | Negative | XSS safety | Enter `<script>` in fields | Rendered escaped, no script execution | | | |
  | NEG-03 | Negative | Unauthorized role | VIEWER edit/create | 403 or denied UI | | | |
  | SEC-01 | Security | CSRF | Submit POST without token | 403 | | | |
  | SEC-02 | Security | Delete via GET | Try GET delete URL | 405/404 | | | |
  | SEC-03 | Security | IDOR decision access | Access decision from other team | 403 | | | |
  | DB-01 | Migration | Migrate cleanly | `alembic upgrade head` | No errors | | | |

**Optional Automated Smoke Tests (Minimal)**

1. `curl -I http://127.0.0.1:8000/` should return 200 after login.
2. `curl -I http://127.0.0.1:8000/kb/status` should return 200.
3. `curl -I http://127.0.0.1:8000/decisions` should return 200 after auth (cookie).
