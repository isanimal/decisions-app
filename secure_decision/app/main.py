from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from .serializers import serialize_decision
from fastapi import Body
from .importer import import_decisions, ImportError



from .db import Base, engine, get_db
from .models import Decision
from .services import create_revision_if_needed, touch_updated_at

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Decision (v0.1)")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    decisions = db.query(Decision).order_by(Decision.updated_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "decisions": decisions})

@app.get("/export/decisions.json")
def export_all_decisions(db: Session = Depends(get_db)):
    decisions = db.query(Decision).order_by(Decision.updated_at.desc()).all()
    data = {
        "format": "secure-decision.export.v0.1",
        "count": len(decisions),
        "decisions": [serialize_decision(d, include_history=True) for d in decisions],
    }
    return JSONResponse(content=data)

@app.post("/import/decisions.json")
def import_decisions_endpoint(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    try:
        result = import_decisions(db, payload)
        return {
            "message": "Decisions imported as draft",
            "result": result,
        }
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/decisions/{decision_id}.json")
def export_one_decision(decision_id: int, db: Session = Depends(get_db)):
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    data = {
        "format": "secure-decision.export.v0.1",
        "decision": serialize_decision(d, include_history=True),
    }
    return JSONResponse(content=data)


@app.get("/decisions/new", response_class=HTMLResponse)
def decision_new(request: Request):
    return templates.TemplateResponse("decision_new.html", {"request": request})


@app.post("/decisions/new")
def decision_create(
    title: str = Form(...),
    context: str = Form(""),
    status: str = Form("draft"),
    technical_goal: str = Form(""),
    assumptions: str = Form(""),
    conscious_simplifications: str = Form(""),
    non_negotiables: str = Form(""),
    accepted_worst_case: str = Form(""),
    db: Session = Depends(get_db),
):
    if status not in ("draft", "active"):
        status = "draft"

    d = Decision(
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
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)


@app.get("/decisions/{decision_id}", response_class=HTMLResponse)
def decision_view(decision_id: int, request: Request, db: Session = Depends(get_db)):
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")

    # show last few revisions (v0.1: optional but useful)
    revisions = d.revisions[:10]
    return templates.TemplateResponse(
        "decision_view.html",
        {"request": request, "d": d, "revisions": revisions},
    )


@app.get("/decisions/{decision_id}/edit", response_class=HTMLResponse)
def decision_edit(decision_id: int, request: Request, db: Session = Depends(get_db)):
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    return templates.TemplateResponse("decision_edit.html", {"request": request, "d": d})


@app.post("/decisions/{decision_id}/edit")
def decision_update(
    decision_id: int,
    title: str = Form(...),
    context: str = Form(""),
    status: str = Form("draft"),
    technical_goal: str = Form(""),
    assumptions: str = Form(""),
    conscious_simplifications: str = Form(""),
    non_negotiables: str = Form(""),
    accepted_worst_case: str = Form(""),
    change_summary: str = Form("Updated decision"),
    db: Session = Depends(get_db),
):
    d = db.get(Decision, decision_id)
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")

    if status not in ("draft", "active"):
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
    touch_updated_at(d)

    # history for active decisions (no blame, no scoring)
    create_revision_if_needed(db, before=before, after=d, change_summary=change_summary.strip() or None)

    db.commit()
    return RedirectResponse(url=f"/decisions/{d.id}", status_code=303)
