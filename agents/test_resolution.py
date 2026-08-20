from agents.resolution_agent import ResolutionAgent


def main():

    print("=" * 70)
    print("RESOLUTION AGENT TEST")
    print("=" * 70)

    print("\nLoading Resolution Agent...")

    agent = ResolutionAgent(top_k=2)

    ticket = """
Subject: Application crashes when I try to open it

Description:
The application crashes immediately after I open it.
I restarted my computer but the problem still happens.
"""

    print("\nGenerating resolution...\n")

    result = agent.generate_resolution(ticket)

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