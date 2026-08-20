from collections import Counter
from loguru import logger


class ClassificationAgent:
    """
    Classifies an IT ticket using historically similar tickets.

    Uses category/subcategory majority voting from RAG results.
    Phi-3 is not required for the default demo pipeline.
    """

    def __init__(self, llm=None):
        self.llm = llm
        logger.info("Classification Agent ready (RAG mode)")

    def classify(self, subject: str, description: str, retrieved_tickets=None):

        if not subject and not description:
            raise ValueError("Subject and description cannot both be empty.")

        if not retrieved_tickets:
            return {
                "category": "General Inquiry",
                "subcategory": "Technical",
                "confidence": 0.0,
                "reason": "No similar historical tickets were found."
            }

        categories = [
            ticket.get("category")
            for ticket in retrieved_tickets
            if ticket.get("category")
        ]

        subcategories = [
            ticket.get("subcategory")
            for ticket in retrieved_tickets
            if ticket.get("subcategory")
        ]

        if categories:
            category_counts = Counter(categories)
            category, category_count = category_counts.most_common(1)[0]
            category_confidence = category_count / len(categories)
        else:
            category = "General Inquiry"
            category_confidence = 0.0

        if subcategories:
            subcategory_counts = Counter(subcategories)
            subcategory, _ = subcategory_counts.most_common(1)[0]
        else:
            subcategory = "Technical"

        confidence = round(category_confidence, 2)

        result = {
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
            "reason": (
                f"Classification is based on {len(retrieved_tickets)} "
                f"historically similar tickets."
            )
        }

        logger.info(
            f"Classification result: "
            f"{category} / {subcategory} "
            f"(confidence={confidence})"
        )

        return result