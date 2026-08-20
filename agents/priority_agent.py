from loguru import logger


class PriorityAgent:
    """
    Determines incident priority using simple business rules
    and information from historically similar tickets.

    Phi-3 is optional and not required for the default demo.
    """

    def __init__(self, llm=None):
        self.llm = llm
        logger.info("Priority Agent ready (rule-based mode)")

    def determine_priority(
        self,
        subject: str,
        description: str,
        retrieved_tickets=None
    ):

        text = f"{subject} {description}".lower()

        # High-priority indicators
        high_keywords = [
            "critical",
            "system down",
            "server down",
            "complete outage",
            "cannot access",
            "security breach",
            "data loss",
            "production down",
            "major outage"
        ]

        # Medium-priority indicators
        medium_keywords = [
            "crash",
            "error",
            "failed",
            "not working",
            "unable",
            "problem",
            "issue",
            "slow",
            "performance"
        ]

        if any(keyword in text for keyword in high_keywords):

            priority = "high"
            confidence = 0.90
            reason = "The incident contains indicators of significant system or business impact."

        elif any(keyword in text for keyword in medium_keywords):

            priority = "medium"
            confidence = 0.80
            reason = "The incident affects functionality but does not indicate a major outage."

        else:

            priority = "low"
            confidence = 0.75
            reason = "The incident appears to be a minor or non-critical request."

        # Use historical tickets as an additional signal
        if retrieved_tickets:

            historical_priorities = []

            for ticket in retrieved_tickets:
                p = ticket.get("priority")

                if p:
                    historical_priorities.append(str(p).lower())

            if historical_priorities:

                high_count = historical_priorities.count("high")
                medium_count = historical_priorities.count("medium")
                low_count = historical_priorities.count("low")

                if high_count > len(historical_priorities) / 2:
                    priority = "high"
                    confidence = max(confidence, 0.85)
                    reason = (
                        "The majority of historically similar incidents "
                        "were classified as high priority."
                    )

                elif medium_count > len(historical_priorities) / 2:
                    priority = "medium"
                    confidence = max(confidence, 0.80)
                    reason = (
                        "The majority of historically similar incidents "
                        "were classified as medium priority."
                    )

                elif low_count > len(historical_priorities) / 2:
                    priority = "low"
                    confidence = max(confidence, 0.75)
                    reason = (
                        "The majority of historically similar incidents "
                        "were classified as low priority."
                    )

        result = {
            "priority": priority,
            "confidence": round(confidence, 2),
            "reason": reason
        }

        logger.info(
            f"Priority result: {priority} "
            f"(confidence={confidence})"
        )

        return result