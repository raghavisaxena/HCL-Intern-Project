from agents.retrieval_agent import RetrievalAgent


def main():

    agent = RetrievalAgent(top_k=5)

    ticket = """
    Subject: Application crashes when I try to open it

    Description:
    The application crashes immediately after I open it.
    I restarted my computer but the problem still happens.
    """

    results = agent.retrieve_for_resolution(ticket)

    print("\n==============================")
    print("RETRIEVAL AGENT")
    print("==============================")

    for i, result in enumerate(results, 1):

        print(f"\n#{i}")
        print(f"Ticket ID: {result['ticket_id']}")
        print(f"Similarity: {result['similarity_score']:.3f}")
        print(f"Subject: {result['subject']}")
        print(f"Category: {result['category']}")
        print(f"Subcategory: {result['subcategory']}")
        print(f"Priority: {result['priority']}")
        print(f"Resolution: {result['resolution']}")


if __name__ == "__main__":
    main()