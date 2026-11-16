from agents.resolution_agent import ResolutionAgent
from agents.retrieval_agent import RetrievalAgent


def main():

    print("=" * 70)
    print("RESOLUTION AGENT TEST")
    print("=" * 70)

    print("\nLoading Resolution Agent...")

    retrieval_agent = RetrievalAgent(top_k=2)

    ticket = """
Subject: Application crashes when I try to open it

Description:
The application crashes immediately after I open it.
I restarted my computer but the problem still happens.
"""

    print("\nGenerating resolution...\n")

    similar_tickets = retrieval_agent.retrieve_for_resolution(ticket)

    agent = ResolutionAgent(top_k=2)

    result = agent.generate_resolution(
        ticket,
        similar_tickets=similar_tickets
    )

    print("=" * 70)
    print("GENERATED RESOLUTION")
    print("=" * 70)

    print(result["resolution"])

    print("\n" + "=" * 70)
    print("SIMILAR HISTORICAL TICKETS")
    print("=" * 70)

    for ticket in result["similar_tickets"]:

        print(
            f"{ticket['ticket_id']} | "
            f"{ticket['category']} | "
            f"{ticket['subcategory']} | "
            f"{ticket['similarity_score']:.3f}"
        )


if __name__ == "__main__":
    main()