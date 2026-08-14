import json
import re
from loguru import logger

from llm.phi_model import Phi3Model


PRIORITIES = [
    "low",
    "medium",
    "high",
]


class PriorityAgent:

    def __init__(self):
        logger.info("Initializing Priority Agent")
        self.llm = Phi3Model()
        logger.info("Priority Agent ready")

    def determine_priority(self, subject: str, description: str) -> dict:

        prompt = f"""
You are an IT support priority assessment agent.

Determine the priority of the following IT support ticket.

SUBJECT:
{subject}

DESCRIPTION:
{description}

Choose EXACTLY ONE priority from:

low
medium
high

Use these guidelines:

HIGH:
- Critical application or system failure
- User cannot perform an important required operation
- Major outage or severe security-related issue
- Issue has significant business impact

MEDIUM:
- Important functionality is affected
- User can continue working with limitations
- Issue requires support but is not critical

LOW:
- General questions
- Minor inconvenience
- Informational requests
- Non-urgent feedback or documentation requests

Return ONLY valid JSON in exactly this format:

{{
  "priority": "low",
  "confidence": 0.0,
  "reason": "short explanation"
}}

Rules:
- Priority must be exactly low, medium, or high.
- Confidence must be a number between 0 and 1.
- Reason must be one short sentence.
- Do not include markdown.
- Do not include any additional fields.
"""

        response = self.llm.generate(
            prompt,
            max_new_tokens=100
        )

        result = self._parse_response(response)

        logger.info(
            f"Priority result: {result['priority']} "
            f"(confidence={result['confidence']})"
        )

        return result

    def _parse_response(self, response: str) -> dict:

        match = re.search(r"\{.*\}", response, re.DOTALL)

        if not match:
            raise ValueError(
                f"Could not find JSON in model response:\n{response}"
            )

        try:
            result = json.loads(match.group())
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON returned by model:\n{response}"
            ) from exc

        priority = result.get("priority")
        confidence = result.get("confidence")
        reason = result.get("reason")

        if priority not in PRIORITIES:
            raise ValueError(
                f"Invalid priority returned by model: {priority}"
            )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid confidence returned by model: {confidence}"
            )

        confidence = max(0.0, min(1.0, confidence))

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Invalid or missing priority reason")

        return {
            "priority": priority,
            "confidence": confidence,
            "reason": reason.strip(),
        }