"""
Ticket analysis endpoint.

This file:
1. Defines the request/response schemas for ticket analysis
2. Loads the SupervisorAgent once at import time (not per-request) so the
   embedding model / FAISS index / Groq client aren't reloaded on every call
3. Exposes POST /api/analyze-ticket, wrapping SupervisorAgent.process_ticket()
"""

import json
import threading
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field

from agents.supervisor_agent import SupervisorAgent
from app.email_service import send_acknowledgment_email, send_resolution_email

router = APIRouter()

logger.info("Loading SupervisorAgent (this may take a moment)...")
supervisor = SupervisorAgent(load_llm=True)
logger.info("SupervisorAgent loaded and ready.")


class TicketRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Short ticket subject/title")
    description: str = Field(..., min_length=1, description="Full ticket description")
    email: str = Field("", description="Optional email for updates")


class TicketResponse(BaseModel):
    ticket: Dict[str, Any]
    classification: Dict[str, Any]
    priority: Dict[str, Any]
    assignment: Dict[str, Any]
    resolution: Dict[str, Any]
    similar_tickets: List[Dict[str, Any]]
    agent_timings: Dict[str, Any] = {}


@router.post("/analyze-ticket", tags=["Tickets"])
async def analyze_ticket(request: TicketRequest):
    """
    Runs the full multi-agent pipeline (classification, priority,
    assignment, resolution, retrieval) on a single ticket and streams
    progress updates as each agent finishes, followed by the final
    combined result.
    """
    logger.info(f"Analyzing ticket: '{request.subject}'")
    email = request.email.strip()
    if email:
        threading.Thread(
            target=send_acknowledgment_email,
            args=(email, f"{request.subject}\n{request.description}"),
            daemon=True,
        ).start()

    def event_stream():
        try:
            for update in supervisor.process_ticket(
                request.subject, request.description
            ):
                yield f"data: {json.dumps(update)}\n\n"
                if update.get("type") == "final" and email:
                    result = update["result"]
                    res = result.get("resolution", {})
                    if isinstance(res, dict):
                        res_text = (
                            res.get("resolution")
                            or res.get("resolution_text")
                            or res.get("text")
                            or json.dumps(res, indent=2)
                        )
                    else:
                        res_text = str(res)
                    threading.Thread(
                        target=send_resolution_email,
                        args=(
                            email,
                            f"{request.subject}\n{request.description}",
                            res_text,
                            result.get("diagnostics") or None,
                        ),
                        daemon=True,
                    ).start()
        except Exception as e:
            logger.exception("Ticket analysis failed")
            error_event = {"type": "error", "detail": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")