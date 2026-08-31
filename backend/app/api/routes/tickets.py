"""
Ticket analysis endpoint.

This file:
1. Defines the request/response schemas for ticket analysis
2. Loads the SupervisorAgent once at import time (not per-request) so the
   embedding model / FAISS index / Groq client aren't reloaded on every call
3. Exposes POST /api/analyze-ticket, wrapping SupervisorAgent.process_ticket()
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
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


@router.post("/analyze-ticket", response_model=TicketResponse, tags=["Tickets"])
async def analyze_ticket(request: TicketRequest):
    """
    Runs the full multi-agent pipeline (classification, priority,
    assignment, resolution, retrieval) on a single ticket and returns
    the combined result.
    """
    logger.info(f"Analyzing ticket: '{request.subject}'")
    try:
        result = supervisor.process_ticket(request.subject, request.description)
        return result
    except Exception as e:
        logger.exception("Ticket analysis failed")
        raise HTTPException(status_code=500, detail=str(e))