# 🚀 Quick Start Guide - Secure Decision App

## Start Server

```bash
cd /Users/macbookpro/testing/Vscode/Decisions/decisions-app/secure_decision
/Users/macbookpro/testing/Vscode/Decisions/.venv/bin/uvicorn app.main:app --reload --port 8000
```

Server: **http://localhost:8000**

---

## API Quick Reference

### Search KB Cards

```bash
curl -X POST http://localhost:8000/kb/match \
  -H "Content-Type: application/json" \
  -d '{
    "decision_pattern": "authentication",
    "tags": ["authentication", "security"],
    "top_k": 5
  }'
```

**Response**: JSON with matched KB cards, ranked by relevance

### View Decisions

```bash
curl http://localhost:8000/decisions
```

### View Single Decision

```bash
curl http://localhost:8000/decisions/1
```

---

## Database

**Location**: `/decisions-app/secure_decision/secure_decision.db`

### Create/Reset Database

```bash
cd /Users/macbookpro/testing/Vscode/Decisions/decisions-app/secure_decision
python scripts/create_tables.py
python scripts/seed_kb_and_decisions.py
```

### Verify Data

```bash
python scripts/verify_data.py
```

---

## What's Included

✅ **10 Decisions** - Real-world architecture decisions  
✅ **12 Threat Assessments** - 6-step threat modeling  
✅ **30 KB Cards** - Security mitigation patterns  
✅ **Searchable API** - Tag-based KB search  
✅ **Web Interface** - Decision viewing and management

---

## Sample Queries

### Microservices Architecture

```bash
curl -X POST http://localhost:8000/kb/match \
  -d '{"decision_pattern": "microservices", "tags": ["microservices"]}'
```

### Authentication & Authorization

```bash
curl -X POST http://localhost:8000/kb/match \
  -d '{"decision_pattern": "auth", "tags": ["authentication"]}'
```

### Kubernetes Deployment

```bash
curl -X POST http://localhost:8000/kb/match \
  -d '{"tags": ["kubernetes"]}'
```

### Database Security

```bash
curl -X POST http://localhost:8000/kb/match \
  -d '{"decision_pattern": "database", "tags": ["database", "security"]}'
```

---

## Database Contents

| Type               | Count | Examples                                   |
| ------------------ | ----- | ------------------------------------------ |
| Decisions          | 10    | Microservices, OAuth2, Kubernetes, etc.    |
| Threat Assessments | 12    | Service impersonation, data exposure, etc. |
| KB Cards           | 30    | mTLS, Circuit Breaker, Rate Limiting, etc. |

---

## Key Features

🔐 **Security-Focused**: 30 proven security patterns  
🔗 **Linked**: Decisions → Threats → Mitigations  
📚 **Knowledge Base**: Practical implementation guides  
🎯 **Searchable**: Find relevant patterns quickly  
📝 **Documentable**: Complete decision records

---

## Need Help?

- **API Errors**: Check server logs during startup
- **Database Issues**: Run `python scripts/create_tables.py`
- **Missing Data**: Run `python scripts/seed_kb_and_decisions.py`
- **Verification**: Run `python scripts/verify_data.py`

---

## Architecture

```
Secure Decision App
├── Frontend (Jinja2 Templates)
│   ├── Decision view & edit
│   └── Threat assessment display
├── API (FastAPI)
│   ├── /kb/match (KB search)
│   ├── /decisions (list/create)
│   └── /decisions/{id}/threat-lite (assessments)
└── Database (SQLite + SQLAlchemy ORM)
    ├── decisions (10)
    ├── threat_lite_assessments (12)
    └── kb_cards (30)
```

---

_Implementation complete. Ready for demo, testing, and deployment._
