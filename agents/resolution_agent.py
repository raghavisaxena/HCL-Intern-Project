from loguru import logger


class ResolutionAgent:
    """
    Generates a resolution using historically similar tickets.

    Default mode:
        RAG -> return the best historical resolution.

    Optional mode:
        Groq (openai/gpt-oss-120b) is used for generative resolution.
    """

    def __init__(self, top_k=3, llm=None):

        logger.info("Initializing Resolution Agent...")

        self.top_k = top_k
        self.llm = llm

        logger.info("Resolution Agent initialized successfully.")

    def generate_resolution(
        self,
        ticket_text: str,
        similar_tickets=None,
        use_llm=False
    ):

        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty.")

        if not similar_tickets:
            return {
                "resolution": (
                    "No similar historical tickets were found. "
                    "Manual investigation is recommended."
                ),
                "similar_tickets": []
            }

        logger.info(
            f"Using {len(similar_tickets)} retrieved tickets "
            f"for resolution."
        )

        # --------------------------------------------------
        # RAG MODE
        # --------------------------------------------------

        if not use_llm:

            best_ticket = max(
                similar_tickets,
                key=lambda x: float(
                    x.get("similarity_score", 0)
                )
            )

            resolution = best_ticket.get("resolution")

            if not resolution:
                resolution = (
                    "A similar historical incident was found, "
                    "but no previous resolution was recorded."
                )

            logger.info(
                "Returning best historical resolution directly (RAG mode)."
            )

            return {
                "resolution": resolution,
                "source_ticket": best_ticket.get("ticket_id"),
                "similar_tickets": similar_tickets,
                "mode": "RAG"
            }

        # --------------------------------------------------
        # OPTIONAL GROQ MODE
        # --------------------------------------------------

        if self.llm is None:
            raise RuntimeError(
                "LLM is not loaded. "
                "Initialize ResolutionAgent with llm=GroqModel() "
                "to use LLM generation."
            )

        context = []

        for ticket in similar_tickets:

            context.append(
                f"""
Ticket ID: {ticket.get('ticket_id')}
Subject: {ticket.get('subject')}
Category: {ticket.get('category')}
Subcategory: {ticket.get('subcategory')}

Previous Resolution:
{ticket.get('resolution')}
"""
            )

        historical_context = "\n".join(context)

        prompt = f"""
You are an IT support resolution assistant.

NEW INCIDENT:
{ticket_text}

HISTORICAL INCIDENTS:
{historical_context}

Based ONLY on the historical examples, provide
clear and practical troubleshooting steps.

Do not invent company-specific information.

Return:

Resolution:
<steps>

Why:
<short explanation>
"""

        logger.info("Generating resolution with Groq...")

        response = self.llm.generate(
            prompt,
            max_new_tokens=300
        )

        return {
            "resolution": response,
            "similar_tickets": similar_tickets,
            "mode": "Groq"
        }