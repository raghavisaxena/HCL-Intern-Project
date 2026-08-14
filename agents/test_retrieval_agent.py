from agents.retrieval_agent import RetrievalAgent


def main():

    agent = RetrievalAgent(top_k=5)

    query = """
    My application crashes every time I try to open it.
    I have restarted the system but the problem still occurs.
    """

    print("\n" + "=" * 70)
    print("NEW INCIDENT")
    print("=" * 70)
    print(query.strip())

    results = agent.retrieve_for_resolution(query)

    print("\n" + "=" * 70)
    print("RETRIEVED HISTORICAL TICKETS")
    print("=" * 70)

    for i, ticket in enumerate(results, start=1):

        print(f"\n#{i}")
        print(f"Ticket ID: {ticket['ticket_id']}")
        print(f"Similarity: {ticket['similarity_score']:.3f}")
        print(f"Subject: {ticket['subject']}")
        print(f"Category: {ticket['category']}")
        print(f"Priority: {ticket['priority']}")
        print(f"Resolution: {ticket['resolution']}")


if __name__ == "__main__":
    main()