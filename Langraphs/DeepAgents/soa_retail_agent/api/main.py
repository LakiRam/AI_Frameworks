"""SOA Retail — production FastAPI runner.

Runs the LangGraph workflow with a SQLite checkpointer so HITL pauses
(via `interrupt_before=["approval"]`) survive across HTTP calls.

Endpoints:
    GET  /              -> HTML UI
    POST /run           -> kick off a run, returns thread_id + state
    POST /approve       -> approve a pending run, returns final plan
    GET  /healthz       -> liveness probe
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from langgraph.checkpoint.sqlite import SqliteSaver

from ..config import API_HOST, API_PORT, CHECKPOINT_DB
from ..graph import build_graph

app = FastAPI(title="SOA Retail Agent", version="0.1.0")

_TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

# Single SqliteSaver shared by the process. Using a file path lets state
# survive container restarts (mount as a volume in production).
_checkpointer = SqliteSaver.from_conn_string(CHECKPOINT_DB)
GRAPH = build_graph(checkpointer=_checkpointer, interrupt_for_approval=True)


def _state_summary(state: dict[str, Any]) -> dict[str, Any]:
    findings = state.get("findings", []) or []
    return {
        "request": state.get("request"),
        "approval_required": state.get("approval_required"),
        "approved": state.get("approved"),
        "plan": state.get("plan"),
        "findings": [
            {
                "agent": f.get("agent"),
                "risk": f.get("risk"),
                "requires_approval": f.get("requires_approval"),
                "summary": (f.get("summary") or "")[:1200],
                "actions": f.get("actions", []),
            }
            for f in findings
        ],
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "result": None}
    )


@app.post("/run")
def run(
    request_text: str = Form(...),
    store_id: str = Form("S001"),
    city: str = Form("Mumbai"),
) -> JSONResponse:
    thread_id = f"soa-{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    inputs = {
        "request": request_text,
        "context": {"store_id": store_id, "city": city},
        "findings": [],
        "messages": [],
    }
    # Stream through; if a HITL interrupt fires, the graph will pause.
    for _ in GRAPH.stream(inputs, cfg):
        pass

    snapshot = GRAPH.get_state(cfg)
    state = dict(snapshot.values) if snapshot else {}
    return JSONResponse(
        {
            "thread_id": thread_id,
            "paused": bool(snapshot.next) if snapshot else False,
            "state": _state_summary(state),
        }
    )


@app.post("/approve")
def approve(thread_id: str = Form(...), approved: bool = Form(True)) -> JSONResponse:
    cfg = {"configurable": {"thread_id": thread_id}}
    # Inject the human decision into state, then resume.
    GRAPH.update_state(cfg, {"approved": approved})
    for _ in GRAPH.stream(None, cfg):
        pass
    snapshot = GRAPH.get_state(cfg)
    state = dict(snapshot.values) if snapshot else {}
    return JSONResponse(
        {
            "thread_id": thread_id,
            "paused": bool(snapshot.next) if snapshot else False,
            "state": _state_summary(state),
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "soa_retail_agent.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
    )
