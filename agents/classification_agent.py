import json
import re
from loguru import logger

from llm.phi_model import Phi3Model


CATEGORIES = [
    "Technical Support",
    "Product Support",
    "Customer Service",
    "IT Support",
    "Billing and Payments",
    "Returns and Exchanges",
    "Service Outages and Maintenance",
    "Sales and Pre-Sales",
    "Human Resources",
    "General Inquiry",
]

SUBCATEGORIES = [
    "Technical",
    "Security",
    "Bug",
    "Feedback",
    "Feature",
    "Billing",
    "Performance",
    "Customer",
    "Crash",
    "Outage",
    "Network",
    "Product",
    "Login",
    "Documentation",
    "Sales",
]


class ClassificationAgent:

    def __init__(self):
        logger.info("Initializing Classification Agent")
        self.llm = Phi3Model()
        logger.info("Classification Agent ready")

    def classify(self, subject: str, description: str) -> dict:

        prompt = f"""
You are an IT support ticket classification agent.

Classify the following IT support ticket.

SUBJECT:
{subject}

DESCRIPTION:
{description}

Choose EXACTLY ONE category from this list:

{", ".join(CATEGORIES)}

Choose EXACTLY ONE subcategory from this list:

{", ".join(SUBCATEGORIES)}

Return ONLY valid JSON in exactly this format:

{{
  "category": "one category from the list",
  "subcategory": "one subcategory from the list",
  "confidence": 0.0
}}

Rules:
- Do not invent category names.
- Do not invent subcategory names.
- Category must exactly match one of the provided categories.
- Subcategory must exactly match one of the provided subcategories.
- Confidence must be a number between 0 and 1.
- Do not include explanations.
- Do not include markdown.
"""

        response = self.llm.generate(
            prompt,
            max_new_tokens=100
        )

        result = self._parse_response(response)

        logger.info(
            f"Classification result: "
            f"{result['category']} / {result['subcategory']} "
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

        category = result.get("category")
        subcategory = result.get("subcategory")
        confidence = result.get("confidence")

        if category not in CATEGORIES:
            raise ValueError(
                f"Invalid category returned by model: {category}"
            )

        if subcategory not in SUBCATEGORIES:
            raise ValueError(
                f"Invalid subcategory returned by model: {subcategory}"
            )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid confidence returned by model: {confidence}"
            )

        confidence = max(0.0, min(1.0, confidence))

        return {
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
        }