"""
Ticket analysis endpoint.

Defines the request/response schemas and exposes
POST /api/analyze-ticket using SupervisorAgent.
"""

import json
from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field

from agents.supervisor_agent import SupervisorAgent

router = APIRouter()

logger.info("Loading SupervisorAgent (this may take a moment)...")
supervisor = SupervisorAgent(load_llm=True)
logger.info("SupervisorAgent loaded and ready.")


class TicketRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Short ticket subject/title")
    description: str = Field(..., min_length=1, description="Full ticket description")


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
    Runs the multi-agent pipeline and streams progress updates
    followed by the final combined result.
    """
    logger.info(f"Analyzing ticket: '{request.subject}'")

    def event_stream():
        try:
            for update in supervisor.process_ticket(
                request.subject, request.description
            ):
                yield f"data: {json.dumps(update)}\n\n"

        except Exception as e:
            logger.exception("Ticket analysis failed")
            error_event = {"type": "error", "detail": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")