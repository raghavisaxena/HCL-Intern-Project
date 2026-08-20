from collections import Counter


class AssignmentRecommendationAgent:
    """
    Recommends the most appropriate support category/subcategory
    using historically similar tickets.
    """

    def recommend(self, retrieved_tickets):
        if not retrieved_tickets:
            return {
                "recommended_category": None,
                "recommended_subcategory": None,
                "confidence": 0.0,
                "reason": "No similar historical tickets were found."
            }

        categories = []
        subcategories = []

        for ticket in retrieved_tickets:
            if ticket.get("category"):
                categories.append(ticket["category"])

            if ticket.get("subcategory"):
                subcategories.append(ticket["subcategory"])

        recommended_category = (
            Counter(categories).most_common(1)[0][0]
            if categories else None
        )

        recommended_subcategory = (
            Counter(subcategories).most_common(1)[0][0]
            if subcategories else None
        )

        # Confidence based on how consistently the retrieved
        # tickets point to the same category.
        if categories:
            category_count = Counter(categories).most_common(1)[0][1]
            confidence = category_count / len(categories)
        else:
            confidence = 0.0

        reason = (
            f"Recommendation is based on {len(retrieved_tickets)} "
            f"historically similar tickets."
        )

        return {
            "recommended_category": recommended_category,
            "recommended_subcategory": recommended_subcategory,
            "confidence": round(confidence, 2),
            "reason": reason
        }