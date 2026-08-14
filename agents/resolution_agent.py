from llm.phi_model import Phi3Model
from agents.retrieval_agent import RetrievalAgent


class ResolutionAgent:
    """
    Generates an IT ticket resolution using:
    - Historical tickets retrieved through FAISS
    - Phi-3 Mini for reasoning and response generation
    """

    def __init__(self, top_k: int = 5):
        self.retrieval_agent = RetrievalAgent(top_k=top_k)
        self.llm = Phi3Model()

    def generate_resolution(self, ticket_text: str):
        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty.")

        historical_tickets = self.retrieval_agent.retrieve_for_resolution(
            ticket_text
        )

        context_parts = []

        for i, ticket in enumerate(historical_tickets, 1):
            context_parts.append(
                f"""
Historical Ticket {i}
Ticket ID: {ticket['ticket_id']}
Subject: {ticket['subject']}
Description: {ticket['description']}
Category: {ticket['category']}
Subcategory: {ticket['subcategory']}
Priority: {ticket['priority']}
Resolution: {ticket['resolution']}
Similarity: {ticket['similarity_score']:.3f}
"""
            )

        historical_context = "\n".join(context_parts)

        prompt = f"""
You are an IT Incident Resolution Assistant.

Analyze the new IT support ticket and use the historical tickets
provided below to suggest an appropriate resolution.

NEW TICKET:
{ticket_text}

HISTORICAL TICKETS:
{historical_context}

Instructions:
- Identify the likely issue.
- Use the historical tickets as supporting evidence.
- Do not blindly copy a historical resolution.
- Adapt the resolution to the new ticket.
- Do not invent technical details that are not supported.
- Give practical troubleshooting steps.
- Keep the response concise and professional.

Provide:
1. Issue Summary
2. Suggested Resolution
3. Troubleshooting Steps
4. Escalation Recommendation (if required)
"""

        return self.llm.generate(prompt, max_new_tokens=300)