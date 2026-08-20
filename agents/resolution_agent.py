from loguru import logger

from agents.retrieval_agent import RetrievalAgent


class ResolutionAgent:
    """
    Generates/returns a resolution for a new IT incident.

    Default behavior:
        Uses RAG to retrieve historically similar tickets and
        immediately returns the best historical resolution.

    Optional behavior:
        Phi-3 Mini can be enabled to generate/refine a resolution
        using the retrieved historical tickets as context.
    """

    def __init__(self, top_k: int = 3, use_llm: bool = False):

        logger.info("Initializing Resolution Agent...")

        self.top_k = top_k
        self.use_llm = use_llm

        # RAG retrieval component
        self.retrieval_agent = RetrievalAgent(top_k=top_k)

        # Load Phi-3 ONLY if explicitly requested
        self.llm = None

        if self.use_llm:
            logger.info("Loading Phi-3 Mini...")

            from llm.phi_model import Phi3Model

            self.llm = Phi3Model()

        logger.info("Resolution Agent initialized successfully.")

    def generate_resolution(self, ticket_text: str):

        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty.")

        # --------------------------------------------------
        # STEP 1: RETRIEVE SIMILAR HISTORICAL TICKETS
        # --------------------------------------------------

        logger.info("Retrieving similar tickets...")

        similar_tickets = self.retrieval_agent.retrieve_for_resolution(
            ticket_text
        )

        if not similar_tickets:

            logger.warning("No similar historical tickets found.")

            return {
                "resolution": (
                    "No similar historical tickets were found. "
                    "Manual investigation is recommended."
                ),
                "similar_tickets": [],
                "source": "fallback"
            }

        logger.info(
            f"Retrieved {len(similar_tickets)} similar tickets."
        )

        # --------------------------------------------------
        # STEP 2: BEST HISTORICAL RESOLUTION
        # --------------------------------------------------

        best_ticket = similar_tickets[0]

        best_resolution = best_ticket.get("resolution", "")

        # If the best ticket does not have a resolution,
        # search the remaining retrieved tickets.
        if not best_resolution or not best_resolution.strip():

            for ticket in similar_tickets[1:]:

                resolution = ticket.get("resolution", "")

                if resolution and resolution.strip():
                    best_ticket = ticket
                    best_resolution = resolution
                    break

        # --------------------------------------------------
        # STEP 3: RAG-ONLY MODE
        # --------------------------------------------------

        if not self.use_llm:

            logger.info(
                "Returning best historical resolution directly "
                "(RAG mode)."
            )

            if best_resolution and best_resolution.strip():

                return {
                    "resolution": best_resolution.strip(),
                    "similar_tickets": similar_tickets,
                    "source": "RAG"
                }

            return {
                "resolution": (
                    "Similar historical incidents were found, "
                    "but no previous resolution is available. "
                    "Manual investigation is recommended."
                ),
                "similar_tickets": similar_tickets,
                "source": "RAG"
            }

        # --------------------------------------------------
        # STEP 4: OPTIONAL PHI-3 GENERATION
        # --------------------------------------------------

        logger.info(
            "Generating refined resolution using Phi-3 Mini..."
        )

        context_parts = []

        for ticket in similar_tickets:

            resolution = ticket.get("resolution", "")

            if resolution:
                resolution = resolution[:500]

            context_parts.append(
                f"""
Ticket ID: {ticket['ticket_id']}
Subject: {ticket['subject']}
Category: {ticket['category']}
Subcategory: {ticket['subcategory']}
Priority: {ticket['priority']}
Similarity: {ticket['similarity_score']:.3f}

Previous Resolution:
{resolution}
"""
            )

        historical_context = "\n".join(context_parts)

        prompt = f"""
You are an IT support assistant.

NEW INCIDENT:
{ticket_text}

HISTORICAL SIMILAR INCIDENTS:
{historical_context}

Based ONLY on the new incident and historical resolutions,
provide a concise practical troubleshooting resolution.

Do not mention AI.
Do not invent company-specific information.
Do not repeat the ticket unnecessarily.

Return only the recommended resolution.
"""

        try:

            response = self.llm.generate(
                prompt,
                max_new_tokens=40
            )

            if response and response.strip():

                logger.info(
                    "Phi-3 generated a resolution successfully."
                )

                return {
                    "resolution": response.strip(),
                    "similar_tickets": similar_tickets,
                    "source": "Phi-3 + RAG"
                }

        except Exception as e:

            logger.error(
                f"Phi-3 generation failed: {e}"
            )

        # --------------------------------------------------
        # STEP 5: FALLBACK TO RAG
        # --------------------------------------------------

        logger.warning(
            "Phi-3 unavailable/failed. "
            "Returning best historical resolution."
        )

        if best_resolution and best_resolution.strip():

            return {
                "resolution": best_resolution.strip(),
                "similar_tickets": similar_tickets,
                "source": "RAG fallback"
            }

        return {
            "resolution": (
                "No usable historical resolution was found. "
                "Manual investigation is recommended."
            ),
            "similar_tickets": similar_tickets,
            "source": "fallback"
        }