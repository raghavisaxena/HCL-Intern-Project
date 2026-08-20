from agents.retrieval_agent import RetrievalAgent
from agents.assignment_agent import AssignmentRecommendationAgent


def main():

    ticket = """
    The application crashes immediately after opening.
    Restarting the computer did not resolve the issue.
    """

    print("Loading Retrieval Agent...")

    retrieval_agent = RetrievalAgent(top_k=5)

    print("Retrieving similar tickets...")

    similar_tickets = retrieval_agent.retrieve_for_resolution(ticket)

    print("\nSimilar tickets found:")
    for ticket in similar_tickets:
        print(
            ticket["ticket_id"],
            "|",
            ticket["category"],
            "|",
            ticket["subcategory"],
            "|",
            round(ticket["similarity_score"], 3)
        )

    print("\nGenerating assignment recommendation...")

    assignment_agent = AssignmentRecommendationAgent()

    recommendation = assignment_agent.recommend(similar_tickets)

    print("\n==============================")
    print("ASSIGNMENT RECOMMENDATION")
    print("==============================")

    print(
        "Recommended Category:",
        recommendation["recommended_category"]
    )

    print(
        "Recommended Subcategory:",
        recommendation["recommended_subcategory"]
    )

    print(
        "Confidence:",
        recommendation["confidence"]
    )

    print(
        "Reason:",
        recommendation["reason"]
    )


if __name__ == "__main__":
    main()