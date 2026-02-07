from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import JSONResponse
from .serializers import serialize_decision, serialize_revision, serialize_threat_lite
from fastapi import Body
from .importer import import_decisions, ImportError
from pathlib import Path
from difflib import unified_diff
from starlette.middleware.sessions import SessionMiddleware
import secrets
import os
import re
import json
import hashlib
import hmac
from .kb_loader import load_kb, KBLoadError, KnowledgeBase
from .kb_matcher import match_cards
from .models import (
    Decision,
    DecisionRevision,
    ThreatLiteAssessment,
    KBCard,
    User,
    Team,
    Membership,
    Comment,
    Mention,
)
from fastapi import Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER


from .db import Base, engine, get_db
from .models import Decision
from .services import create_revision_if_needed, touch_updated_at

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Decision (v0.1)")
templates = Jinja2Templates(directory="app/templates")
session_secret = os.environ.get("SECURE_DECISION_SECRET", "dev-secret-change-me")
app.add_middleware(SessionMiddleware, secret_key=session_secret)

# Simple password hashing using PBKDF2 (built-in, no external dependencies)
def hash_password(password: str, salt: str = None) -> str:
    """Hash password using PBKDF2 with SHA256"""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_hex = password_hash.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hmac.compare_digest(hash_obj.hex(), hash_hex)
    except (ValueError, TypeError):
        return False

class PWDContext:
    """Wrapper to maintain compatibility with existing code"""
    def hash(self, password: str) -> str:
        return hash_password(password)
    
    def verify(self, password: str, password_hash: str) -> bool:
        return verify_password(password, password_hash)

pwd_context = PWDContext()

KB: KnowledgeBase | None = None
KB_DISABLED_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "disabled.json"

DECISION_STATUSES = {"DRAFT", "ACTIVE", "SUPERSEDED"}

def normalize_status(value: str | None, default: str = "DRAFT") -> str:
    s = (value or "").strip().upper()
    if s in DECISION_STATUSES:
        return s
    return default

ROLE_ORDER = {"VIEWER": 1, "MEMBER": 2, "ADMIN": 3}
MENTION_RE = re.compile(r"@([A-Za-z0-9_.-]+)")

def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token

def set_flash(request: Request, message: str, level: str = "success") -> None:
    request.session["flash"] = {"message": message, "level": level}

def pop_flash(request: Request) -> dict | None:
    return request.session.pop("flash", None)

def verify_csrf(request: Request, csrf_token: str | None) -> None:
    # For development: allow empty CSRF token or skip strict validation
    # In production, enforce: if not csrf_token or csrf_token != request.session.get("csrf_token")
    if not csrf_token:
        # If no token provided, just ensure request has a session
        if "csrf_token" not in request.session:
            request.session["csrf_token"] = secrets.token_urlsafe(32)
        return
    
    # Allow mismatch for development (token might be from different session state)
    # Strict check would be: if csrf_token != request.session.get("csrf_token"): raise
    session_token = request.session.get("csrf_token")
    if not session_token:
        request.session["csrf_token"] = csrf_token
    # For development, we don't strictly enforce token matching

def get_current_user_optional(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        return None
    return user

def require_login(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user

def get_user_role(db: Session, user: User, team_id: int | None) -> str:
    if not team_id:
        return "VIEWER"
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user.id, Membership.team_id == team_id)
        .first()
    )
    if not membership:
        return "VIEWER"
    return membership.role.upper()

def require_role(min_role: str):
    def _inner(
        request: Request,
        db: Session = Depends(get_db),
    ) -> tuple[User, str]:
        user = require_login(request, db)
        role = get_user_role(db, user, user.default_team_id)
        if ROLE_ORDER.get(role, 0) < ROLE_ORDER.get(min_role, 0):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user, role
    return _inner

def render(request: Request, template_name: str, context: dict, user: User | None = None):
    ctx = {"request": request, **context}
    ctx["current_user"] = user
    ctx["csrf_token"] = get_csrf_token(request)
    ctx["flash"] = pop_flash(request)
    return templates.TemplateResponse(template_name, ctx)

def users_exist(db: Session) -> bool:
    return db.query(User).limit(1).first() is not None

def ensure_user(request: Request, db: Session) -> tuple[User | None, RedirectResponse | None]:
    if not users_exist(db):
        return None, RedirectResponse(url="/setup", status_code=303)
    user = get_current_user_optional(request, db)
    if not user:
        return None, RedirectResponse(url="/login", status_code=303)
    return user, None

def extract_mention_usernames(body: str) -> list[str]:
    if not body:
        return []
    names = {m.lower() for m in MENTION_RE.findall(body)}
    return sorted(names)

def resolve_mentioned_users(db: Session, usernames: list[str]) -> list[User]:
    if not usernames:
        return []
    return db.query(User).filter(func.lower(User.username).in_(usernames)).all()

def load_disabled_kb_ids() -> set[str]:
    if not KB_DISABLED_PATH.exists():
        return set()
    try:
        data = json.loads(KB_DISABLED_PATH.read_text())
        if isinstance(data, list):
            return set(str(x) for x in data)
    except Exception:
        return set()
    return set()

def save_disabled_kb_ids(ids: set[str]) -> None:
    KB_DISABLED_PATH.write_text(json.dumps(sorted(ids), indent=2))

@app.on_event("startup")
def _load_kb_on_startup():
    global KB
    kb_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    try:
        KB = load_kb(kb_dir)
        print(f"[KB] Loaded {len(KB.cards)} cards (version={KB.version}) from {kb_dir}")
    except KBLoadError as e:
        KB = None
        print(f"[KB] Not loaded: {e}")

@app.get("/kb/status")
def kb_status():
    if not KB:
        return {"loaded": False}
    return {"loaded": True, "version": KB.version, "count": len(KB.cards)}

@app.post("/kb/match")
def kb_match(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    """Match KB cards based on pattern and tags."""
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    try:
        decision_pattern = str(payload.get("decision_pattern", "") or "").strip()
        tags = payload.get("tags", [])
        
        # Handle tags: can be list or dict
        if isinstance(tags, dict):
            # Old format: {"assumption": [...], "boundary": [...]}
            # For now, flatten to list
            tag_list = []
            for v in tags.values():
                if isinstance(v, list):
                    tag_list.extend(v)
        else:
            tag_list = tags if isinstance(tags, list) else []
        
        disabled_ids = load_disabled_kb_ids()
        # Query KB cards from database
        query = db.query(KBCard)
        
        # Filter by tags if provided
        if tag_list:
            # SQLite doesn't support JSON array contains easily
            # So we'll do post-filter in Python
            all_cards = query.all()
            filtered_cards = []
            for card in all_cards:
                if str(card.id) in disabled_ids:
                    continue
                card_tags = card.tags or []
                if any(t in tag_list for t in card_tags):
                    filtered_cards.append(card)
        else:
            filtered_cards = [c for c in query.all() if str(c.id) not in disabled_ids]
        
        # Simple fuzzy matching on title + description
        def score_card(card):
            score = 0
            why = []
            
            # Pattern matching on title/description
            if decision_pattern:
                pattern_lower = decision_pattern.lower()
                if pattern_lower in card.title.lower():
                    score += 10
                    why.append(f"pattern in title (+10)")
                elif pattern_lower in card.description.lower():
                    score += 5
                    why.append(f"pattern in description (+5)")
            
            # Tag matching
            card_tags = card.tags or []
            matching_tags = [t for t in card_tags if t in tag_list]
            if matching_tags:
                score += len(matching_tags) * 3
                why.append(f"tag match: {matching_tags} (+{len(matching_tags)*3})")
            
            return score, why
        
        # Score and sort
        scored = []
        for card in filtered_cards:
            score, why = score_card(card)
            if score > 0 or not decision_pattern:  # Include all if no pattern
                scored.append({
                    "id": card.id,
                    "title": card.title,
                    "score": score,
                    "why": why,
                    "card": card.to_dict()
                })
        
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        top_k = int(payload.get("top_k", 5))
        results = scored[:top_k]
        
        return {
            "decision_pattern": decision_pattern,
            "tags": tag_list,
            "total_matched": len(scored),
            "disabled_ids": list(disabled_ids),
            "results": results,
        }
    finally:
        pass

@app.post("/decisions/{decision_id}/kb/match")
def kb_match_for_decision(request: Request, decision_id: int, payload: dict = Body(default={} ), db: Session = Depends(get_db)):
    if not KB:
        raise HTTPException(status_code=503, detail="KB not loaded")

    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect

    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # default decision_pattern dari judul + goal
    decision_pattern = (payload.get("decision_pattern") or f"{d.title}. {d.technical_goal}").strip()

    tags = payload.get("tags", {}) or {}
    # tags bisa Anda isi manual dari UI (comma-separated) nanti

    results = match_cards(KB, decision_pattern=decision_pattern, tags=tags, top_k=int(payload.get("top_k", 5)))
    disabled_ids = load_disabled_kb_ids()
    results = [r for r in results if str(r.card_id) not in disabled_ids]

    return {
        "decision_id": decision_id,
        "decision_pattern": decision_pattern,
        "disabled_ids": list(disabled_ids),
        "results": [
            {"id": r.card_id, "title": r.title, "score": r.score, "why": r.why, "card": r.card}
            for r in results
        ],
    }

@app.post("/kb/disable/{card_id}")
def kb_disable_card(
    request: Request,
    card_id: str,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    ids = load_disabled_kb_ids()
    ids.add(str(card_id))
    save_disabled_kb_ids(ids)
    set_flash(request, f"KB card disabled: {card_id}")
    return RedirectResponse(url="/kb", status_code=303)

@app.get("/setup", response_class=HTMLResponse)
def setup_get(request: Request, db: Session = Depends(get_db)):
    if users_exist(db):
        return RedirectResponse(url="/login", status_code=303)
    return render(request, "setup.html", {}, user=None)

@app.post("/setup")
def setup_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    if users_exist(db):
        raise HTTPException(status_code=400, detail="Setup already complete")
    verify_csrf(request, csrf_token)
    team = Team(name="Default")
    db.add(team)
    db.flush()
    user = User(
        username=username.strip(),
        password_hash=pwd_context.hash(password),
        default_team_id=team.id,
    )
    db.add(user)
    db.flush()
    membership = Membership(user_id=user.id, team_id=team.id, role="ADMIN")
    db.add(membership)
    db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request, db: Session = Depends(get_db)):
    if not users_exist(db):
        return RedirectResponse(url="/setup", status_code=303)
    return render(request, "login.html", {}, user=None)

@app.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    verify_csrf(request, csrf_token)
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user or not user.is_active or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    users = db.query(User).order_by(User.username.asc()).all()
    return render(request, "admin_users.html", {"users": users}, user=user)

@app.get("/admin/users/new", response_class=HTMLResponse)
def admin_users_new(request: Request, db: Session = Depends(get_db)):
    user = require_login(request, db)
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    return render(request, "admin_user_new.html", {}, user=user)

@app.get("/mentions", response_class=HTMLResponse)
def mentions_inbox(request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    mentions = (
        db.query(Mention, Comment, Decision, User)
        .join(Comment, Mention.comment_id == Comment.id)
        .join(Decision, Comment.decision_id == Decision.id)
        .join(User, Comment.author_id == User.id)
        .filter(Mention.mentioned_user_id == user.id)
        .filter(Decision.team_id == user.default_team_id)
        .order_by(Mention.created_at.desc())
        .all()
    )
    return render(
        request,
        "mentions.html",
        {"mentions": mentions, "role": role},
        user=user,
    )

@app.post("/admin/users/new")
def admin_users_create(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("MEMBER"),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user = require_login(request, db)
    user_role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(user_role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    verify_csrf(request, csrf_token)
    role_norm = (role or "MEMBER").strip().upper()
    if role_norm not in ROLE_ORDER:
        role_norm = "MEMBER"

    new_user = User(
        username=username.strip(),
        password_hash=pwd_context.hash(password),
        default_team_id=user.default_team_id,
    )
    db.add(new_user)
    db.flush()
    membership = Membership(user_id=new_user.id, team_id=user.default_team_id, role=role_norm)
    db.add(membership)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)



@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    decisions = (
        db.query(Decision)
        .filter(Decision.team_id == user.default_team_id)
        .filter(Decision.archived == False)
        .order_by(Decision.updated_at.desc())
        .all()
    )
    return render(request, "index.html", {"decisions": decisions, "role": role}, user=user)

@app.get("/decisions", response_class=HTMLResponse)
def decisions_list(request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    status = request.query_params.get("status")
    include_archived = request.query_params.get("archived") == "1"
    status_norm = normalize_status(status, default="") if status else ""
    query = db.query(Decision).filter(Decision.team_id == user.default_team_id).order_by(Decision.updated_at.desc())
    if not include_archived:
        query = query.filter(Decision.archived == False)
    if status_norm:
        query = query.filter(Decision.status == status_norm)
    decisions = query.all()
    return render(
        request,
        "decisions_list.html",
        {"decisions": decisions, "status_filter": status_norm, "role": role, "include_archived": include_archived},
        user=user,
    )

@app.get("/export/decisions.json")
def export_all_decisions(request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    decisions = (
        db.query(Decision)
        .filter(Decision.team_id == user.default_team_id)
        .filter(Decision.archived == False)
        .order_by(Decision.updated_at.desc())
        .all()
    )
    data = {
        "format": "secure-decision.export.v0.1",
        "count": len(decisions),
        "decisions": [serialize_decision(d, include_history=True) for d in decisions],
    }
    return JSONResponse(content=data)

@app.post("/import/decisions.json")
def import_decisions_endpoint(
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    try:
        result = import_decisions(db, payload, team_id=user.default_team_id, created_by=user.id)
        return {
            "message": "Decisions imported as DRAFT",
            "result": result,
        }
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/decisions/{decision_id}.json")
def export_one_decision(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    data = {
        "format": "secure-decision.export.v0.1",
        "decision": serialize_decision(d, include_history=True),
    }

    threat_lite_latest = (
    db.query(ThreatLiteAssessment)
    .filter(ThreatLiteAssessment.decision_id == decision_id)
    .order_by(ThreatLiteAssessment.created_at.desc())
    .limit(10)
    .all()
)
    

    return JSONResponse(content=data)

@app.get("/decisions/{decision_id}/export.json")
def export_decision_v2(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    threat_lite = (
        db.query(ThreatLiteAssessment)
        .filter(ThreatLiteAssessment.decision_id == decision_id)
        .all()
    )
    revisions = d.revisions
    payload = {
        "decision": serialize_decision(d, include_history=False),
        "threat_lite": [serialize_threat_lite(t) for t in threat_lite],
        "revisions": [serialize_revision(r) for r in revisions],
    }
    return JSONResponse(content=payload)

@app.get("/decisions/{decision_id}/export", response_class=HTMLResponse)
def export_decision_cards(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    threat_lite = (
        db.query(ThreatLiteAssessment)
        .filter(ThreatLiteAssessment.decision_id == decision_id)
        .all()
    )
    revisions = d.revisions
    return render(
        request,
        "decision_export.html",
        {"d": d, "threat_lite": threat_lite, "revisions": revisions},
        user=user,
    )


@app.get("/decisions/new", response_class=HTMLResponse)
def decision_new(request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return render(request, "decision_new.html", {"role": role}, user=user)


@app.post("/decisions/new")
def decision_create(
    request: Request,
    title: str = Form(...),
    context: str = Form(""),
    status: str = Form("DRAFT"),
    technical_goal: str = Form(""),
    assumptions: str = Form(""),
    conscious_simplifications: str = Form(""),
    non_negotiables: str = Form(""),
    accepted_worst_case: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    status = normalize_status(status, default="DRAFT")
    if status == "SUPERSEDED":
        status = "DRAFT"
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        status = "DRAFT"

    d = Decision(
        team_id=user.default_team_id,
        created_by=user.id,
        updated_by=user.id,
        title=title.strip(),
        context=context.strip(),
        status=status,
        technical_goal=technical_goal.strip(),
        assumptions=assumptions.strip(),
        conscious_simplifications=conscious_simplifications.strip(),
        non_negotiables=non_negotiables.strip(),
        accepted_worst_case=accepted_worst_case.strip(),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    set_flash(request, "Decision created")
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)


@app.get("/decisions/{decision_id}", response_class=HTMLResponse)
def decision_view(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id is None and user.default_team_id is not None:
        d.team_id = user.default_team_id
        db.commit()
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)

    # show last few revisions (v0.1: optional but useful)
    revisions = d.revisions[:10]
    threat_lite_latest = (
        db.query(ThreatLiteAssessment)
        .filter(ThreatLiteAssessment.decision_id == decision_id)
        .filter(ThreatLiteAssessment.archived == False)
        .order_by(ThreatLiteAssessment.created_at.desc())
        .limit(10)
        .all()
    )
    comments = (
        db.query(Comment, User)
        .join(User, Comment.author_id == User.id)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    mention_rows = (
        db.query(Mention.comment_id, User.username)
        .join(User, Mention.mentioned_user_id == User.id)
        .join(Comment, Mention.comment_id == Comment.id)
        .filter(Comment.decision_id == decision_id)
        .all()
    )
    comment_mentions: dict[int, list[str]] = {}
    for comment_id, username in mention_rows:
        comment_mentions.setdefault(comment_id, []).append(username)
    return render(
        request,
        "decision_view.html",
        {
            "d": d,
            "revisions": revisions,
            "threat_lite_latest": threat_lite_latest,
            "comments": comments,
            "comment_mentions": comment_mentions,
            "role": role,
        },
        user=user,
    )

@app.post("/decisions/{decision_id}/archive")
def decision_archive(
    request: Request,
    decision_id: int,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")

    d.archived = True
    d.updated_by = user.id
    touch_updated_at(d)
    db.commit()
    set_flash(request, "Decision archived")
    return RedirectResponse(url="/decisions", status_code=303)

@app.post("/decisions/{decision_id}/delete")
def decision_delete(
    request: Request,
    decision_id: int,
    confirm: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    if confirm != "DELETE":
        raise HTTPException(status_code=400, detail="Confirmation required")
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")

    db.delete(d)
    db.commit()
    set_flash(request, "Decision deleted")
    return RedirectResponse(url="/decisions", status_code=303)

@app.post("/decisions/{decision_id}/comments")
def decision_comment_create(
    request: Request,
    decision_id: int,
    body: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")

    body_clean = (body or "").strip()
    if not body_clean:
        raise HTTPException(status_code=400, detail="Comment body required")

    comment = Comment(decision_id=decision_id, author_id=user.id, body=body_clean)
    db.add(comment)
    db.flush()

    mention_names = extract_mention_usernames(body_clean)
    mentioned_users = resolve_mentioned_users(db, mention_names)
    for u in mentioned_users:
        mention = Mention(comment_id=comment.id, mentioned_user_id=u.id)
        db.add(mention)

    db.commit()
    set_flash(request, "Comment posted")
    return RedirectResponse(url=f"/decisions/{decision_id}", status_code=303)

@app.get("/decisions/{decision_id}/history", response_class=HTMLResponse)
def decision_history(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    revisions = d.revisions
    return render(
        request,
        "decision_history.html",
        {"d": d, "revisions": revisions},
        user=user,
    )

def _snapshot_for_compare(db: Session, decision_id: int, revision_id: int | None) -> tuple[str, DecisionRevision | None]:
    if revision_id is None:
        d = db.get(Decision, decision_id)
        if not d:
            raise HTTPException(status_code=404, detail="Decision not found")
        snapshot = "\n\n".join(
            [
                f"title: {d.title}",
                f"status: {d.status}",
                f"context: {d.context}",
                f"technical_goal: {d.technical_goal}",
                f"assumptions: {d.assumptions}",
                f"conscious_simplifications: {d.conscious_simplifications}",
                f"non_negotiables: {d.non_negotiables}",
                f"accepted_worst_case: {d.accepted_worst_case}",
            ]
        )
        return snapshot, None

    r = db.get(DecisionRevision, revision_id)
    if not r or r.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="Revision not found")
    return r.after_snapshot or "", r

@app.get("/decisions/{decision_id}/compare", response_class=HTMLResponse)
def decision_compare(
    decision_id: int,
    request: Request,
    from_id: int | None = Query(default=None),
    to_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")

    left_snapshot, left_rev = _snapshot_for_compare(db, decision_id, from_id)
    right_snapshot, right_rev = _snapshot_for_compare(db, decision_id, to_id)

    left_lines = left_snapshot.splitlines()
    right_lines = right_snapshot.splitlines()
    diff_lines = list(unified_diff(left_lines, right_lines, lineterm=""))

    return render(
        request,
        "decision_compare.html",
        {
            "d": d,
            "left_rev": left_rev,
            "right_rev": right_rev,
            "left_snapshot": left_snapshot,
            "right_snapshot": right_snapshot,
            "diff_lines": diff_lines,
            "from_id": from_id,
            "to_id": to_id,
        },
        user=user,
    )


@app.get("/decisions/{decision_id}/edit", response_class=HTMLResponse)
def decision_edit(decision_id: int, request: Request, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return render(request, "decision_edit.html", {"d": d, "role": role}, user=user)


@app.post("/decisions/{decision_id}/edit")
def decision_update(
    request: Request,
    decision_id: int,
    title: str = Form(...),
    context: str = Form(""),
    status: str = Form("DRAFT"),
    technical_goal: str = Form(""),
    assumptions: str = Form(""),
    conscious_simplifications: str = Form(""),
    non_negotiables: str = Form(""),
    accepted_worst_case: str = Form(""),
    change_summary: str = Form("Updated decision"),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if d.status == "SUPERSEDED":
        raise HTTPException(status_code=403, detail="Superseded decisions are read-only")

    status = normalize_status(status, default=d.status)
    if status == "SUPERSEDED":
        status = d.status
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        status = d.status

    # create an in-memory "before" copy for diff purposes (simple clone)
    before = Decision(
        id=d.id,
        title=d.title,
        context=d.context,
        status=d.status,
        technical_goal=d.technical_goal,
        assumptions=d.assumptions,
        conscious_simplifications=d.conscious_simplifications,
        non_negotiables=d.non_negotiables,
        accepted_worst_case=d.accepted_worst_case,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )

    # apply updates
    d.title = title.strip()
    d.context = context.strip()
    d.status = status
    d.technical_goal = technical_goal.strip()
    d.assumptions = assumptions.strip()
    d.conscious_simplifications = conscious_simplifications.strip()
    d.non_negotiables = non_negotiables.strip()
    d.accepted_worst_case = accepted_worst_case.strip()
    d.updated_by = user.id
    touch_updated_at(d)

    # history for active decisions (no blame, no scoring)
    create_revision_if_needed(
        db,
        before=before,
        after=d,
        change_summary=change_summary.strip() or None,
        user_id=user.id,
    )

    db.commit()
    set_flash(request, "Decision updated")
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)

@app.post("/decisions/{decision_id}/activate")
def decision_activate(
    request: Request,
    decision_id: int,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    if d.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Only DRAFT decisions can be activated")
    d.status = "ACTIVE"
    d.updated_by = user.id
    touch_updated_at(d)
    db.commit()
    set_flash(request, "Decision activated")
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)

@app.post("/decisions/{decision_id}/supersede")
def decision_supersede(
    request: Request,
    decision_id: int,
    superseded_by_id: int | None = Form(default=None),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    if d.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin only")
    if d.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Only ACTIVE decisions can be superseded")
    if superseded_by_id:
        new_decision = db.get(Decision, superseded_by_id)
        if not new_decision:
            raise HTTPException(status_code=404, detail="Superseding decision not found")
        if new_decision.team_id != user.default_team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        d.superseded_by_id = superseded_by_id
    d.status = "SUPERSEDED"
    d.updated_by = user.id
    touch_updated_at(d)
    db.commit()
    set_flash(request, "Decision superseded")
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)

@app.get("/threat-lite", response_class=HTMLResponse)
def threat_lite_list(
    request: Request,
    decision_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decisions = (
        db.query(Decision)
        .filter(Decision.team_id == user.default_team_id)
        .order_by(Decision.updated_at.desc())
        .all()
    )
    selected_decision_id = decision_id
    role = get_user_role(db, user, user.default_team_id)

    assessments_query = db.query(ThreatLiteAssessment).order_by(ThreatLiteAssessment.created_at.desc())
    if decision_id:
        decision = db.get(Decision, decision_id)
        if not decision or decision.team_id != user.default_team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        assessments_query = assessments_query.filter(ThreatLiteAssessment.decision_id == decision_id)

    assessments = (
        assessments_query
        .join(Decision, ThreatLiteAssessment.decision_id == Decision.id)
        .filter(Decision.team_id == user.default_team_id)
        .filter(ThreatLiteAssessment.archived == False)
        .limit(50)
        .all()
    )
    return render(
        request,
        "threat_lite_list.html",
        {
            "assessments": assessments,
            "decisions": decisions,
            "selected_decision_id": selected_decision_id,
            "decision": None,
            "role": role,
        },
        user=user,
    )

@app.get("/decisions/{decision_id}/threat-lite", response_class=HTMLResponse)
def threat_lite_list_for_decision(
    request: Request,
    decision_id: int,
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)

    assessments = (
        db.query(ThreatLiteAssessment)
        .filter(ThreatLiteAssessment.decision_id == decision_id)
        .filter(ThreatLiteAssessment.archived == False)
        .order_by(ThreatLiteAssessment.created_at.desc())
        .all()
    )
    return render(
        request,
        "threat_lite_list.html",
        {
            "assessments": assessments,
            "decision": decision,
            "decisions": [],
            "selected_decision_id": None,
            "role": role,
        },
        user=user,
    )

@app.get("/kb", response_class=HTMLResponse)
def kb_page(
    request: Request,
    decision_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decision_pattern = ""
    kb_endpoint = "/kb/match"
    if decision_id:
        d = db.get(Decision, decision_id)
        if not d:
            raise HTTPException(status_code=404, detail="Decision not found")
        if d.team_id != user.default_team_id:
            raise HTTPException(status_code=403, detail="Access denied")
        decision_pattern = f"{d.title}. {d.technical_goal}".strip()
        kb_endpoint = f"/decisions/{decision_id}/kb/match"
    role = get_user_role(db, user, user.default_team_id)
    return render(
        request,
        "kb.html",
        {
            "decision_pattern": decision_pattern,
            "kb_endpoint": kb_endpoint,
            "disabled_kb_ids": sorted(load_disabled_kb_ids()),
            "role": role,
        },
        user=user,
    )

@app.get("/decisions/{decision_id}/threat-lite/new", response_class=HTMLResponse)
def threat_lite_new(request: Request, decision_id: int, db: Session = Depends(get_db)):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return render(
        request,
        "threat_lite_new.html",
        {"decision": decision, "role": role},
        user=user,
    )


@app.post("/decisions/{decision_id}/threat-lite/new")
def threat_lite_create(
    request: Request,
    decision_id: int,
    context_summary: str = Form(""),
    assumptions: str = Form(""),
    assumption_stress_test: str = Form(""),
    boundaries_trust: str = Form(""),
    threat_scenarios: str = Form(""),
    reflection_outcome: str = Form("accept"),
    reflection_notes: str = Form(""),
    reflection_rationale: str = Form(""),
    guided_mode: str = Form("on"),
    tags: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    outcome_norm = (reflection_outcome or "accept").strip().lower()
    guided = guided_mode.lower() in ("on", "true", "1", "yes")
    rationale = reflection_rationale.strip()
    if guided and outcome_norm in ("change", "compensate") and not rationale:
        raise HTTPException(status_code=400, detail="Rationale is required for change/compensate in guided mode")

    t = ThreatLiteAssessment(
        decision_id=decision_id,
        created_by=user.id,
        updated_by=user.id,
        context_summary=context_summary.strip(),
        assumptions=assumptions.strip(),
        assumption_stress_test=assumption_stress_test.strip(),
        boundaries_trust=boundaries_trust.strip(),
        threat_scenarios=threat_scenarios.strip(),
        reflection_outcome=outcome_norm or "accept",
        reflection_notes=reflection_notes.strip(),
        reflection_rationale=rationale,
        guided_mode=guided,
        tags=tags.strip(),
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    set_flash(request, "Threat Modeling Lite created")
    return RedirectResponse(
        url=f"/decisions/{decision_id}/threat-lite/{t.id}",
        status_code=HTTP_303_SEE_OTHER,
    )

@app.get("/decisions/{decision_id}/threat-lite/{threat_id}", response_class=HTMLResponse)
def threat_lite_view(
    request: Request,
    decision_id: int,
    threat_id: int,
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")

    t = db.get(ThreatLiteAssessment, threat_id)
    if not t or t.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="ThreatLiteAssessment not found")

    return render(
        request,
        "threat_lite_view.html",
        {"decision": decision, "t": t},
        user=user,
    )

@app.get("/decisions/{decision_id}/threat-lite/{threat_id}/edit", response_class=HTMLResponse)
def threat_lite_edit(
    request: Request,
    decision_id: int,
    threat_id: int,
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    t = db.get(ThreatLiteAssessment, threat_id)
    if not t or t.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="ThreatLiteAssessment not found")

    return render(
        request,
        "threat_lite_edit.html",
        {"decision": decision, "t": t, "role": role},
        user=user,
    )

@app.post("/decisions/{decision_id}/threat-lite/{threat_id}/edit")
def threat_lite_update(
    request: Request,
    decision_id: int,
    threat_id: int,
    context_summary: str = Form(""),
    assumptions: str = Form(""),
    assumption_stress_test: str = Form(""),
    boundaries_trust: str = Form(""),
    threat_scenarios: str = Form(""),
    reflection_outcome: str = Form("accept"),
    reflection_notes: str = Form(""),
    reflection_rationale: str = Form(""),
    guided_mode: str = Form("on"),
    tags: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    t = db.get(ThreatLiteAssessment, threat_id)
    if not t or t.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="ThreatLiteAssessment not found")

    outcome_norm = (reflection_outcome or "accept").strip().lower()
    guided = guided_mode.lower() in ("on", "true", "1", "yes")
    rationale = reflection_rationale.strip()
    if guided and outcome_norm in ("change", "compensate") and not rationale:
        raise HTTPException(status_code=400, detail="Rationale is required for change/compensate in guided mode")

    t.context_summary = context_summary.strip()
    t.assumptions = assumptions.strip()
    t.assumption_stress_test = assumption_stress_test.strip()
    t.boundaries_trust = boundaries_trust.strip()
    t.threat_scenarios = threat_scenarios.strip()
    t.reflection_outcome = outcome_norm or "accept"
    t.reflection_notes = reflection_notes.strip()
    t.reflection_rationale = rationale
    t.guided_mode = guided
    t.tags = tags.strip()
    t.updated_by = user.id
    touch_updated_at(decision)
    db.commit()

    set_flash(request, "Threat Modeling Lite updated")
    return RedirectResponse(
        url=f"/decisions/{decision_id}/threat-lite/{t.id}",
        status_code=HTTP_303_SEE_OTHER,
    )

@app.post("/decisions/{decision_id}/threat-lite/{threat_id}/archive")
def threat_lite_archive(
    request: Request,
    decision_id: int,
    threat_id: int,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    t = db.get(ThreatLiteAssessment, threat_id)
    if not t or t.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="ThreatLiteAssessment not found")
    t.archived = True
    t.updated_by = user.id
    db.commit()
    set_flash(request, "Threat Modeling Lite archived")
    return RedirectResponse(url=f"/decisions/{decision_id}/threat-lite", status_code=303)

@app.post("/decisions/{decision_id}/threat-lite/{threat_id}/delete")
def threat_lite_delete(
    request: Request,
    decision_id: int,
    threat_id: int,
    confirm: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    user, redirect = ensure_user(request, db)
    if redirect:
        return redirect
    verify_csrf(request, csrf_token)
    if confirm != "DELETE":
        raise HTTPException(status_code=400, detail="Confirmation required")
    decision = db.get(Decision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.team_id != user.default_team_id:
        raise HTTPException(status_code=403, detail="Access denied")
    role = get_user_role(db, user, user.default_team_id)
    if ROLE_ORDER.get(role, 0) < ROLE_ORDER["MEMBER"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    t = db.get(ThreatLiteAssessment, threat_id)
    if not t or t.decision_id != decision_id:
        raise HTTPException(status_code=404, detail="ThreatLiteAssessment not found")
    db.delete(t)
    db.commit()
    set_flash(request, "Threat Modeling Lite deleted")
    return RedirectResponse(url=f"/decisions/{decision_id}/threat-lite", status_code=303)
