from agents.supervisor_agent import SupervisorAgent


def main():

    print("=" * 70)
    print("              IT INCIDENT ASSISTANT")
    print("              SUPERVISOR AGENT DEMO")
    print("=" * 70)

    subject = "Application crashes when I try to open it"

    description = (
        "The application crashes immediately after I open it. "
        "I restarted my computer but the problem still happens."
    )

    print("\nNEW INCIDENT")
    print("-" * 70)

    print(f"Subject: {subject}")
    print(f"Description: {description}")

    print("\n")
    print("Loading Supervisor Agent...")

    # IMPORTANT:
    # load_llm=False keeps the demo fast.
    supervisor = SupervisorAgent(
        load_llm=False
    )

    print("\nProcessing incident...")
    print("-" * 70)

    result = supervisor.process_ticket(
        subject,
        description
    )

    # --------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("                    FINAL RESULT")
    print("=" * 70)

    print("\nCLASSIFICATION")
    print("-" * 70)

    classification = result["classification"]

    print(
        f"Category      : "
        f"{classification['category']}"
    )

    print(
        f"Subcategory   : "
        f"{classification['subcategory']}"
    )

    print(
        f"Confidence    : "
        f"{classification['confidence']}"
    )

    print(
        f"Reason        : "
        f"{classification['reason']}"
    )

    print("\nPRIORITY")
    print("-" * 70)

    priority = result["priority"]

    print(
        f"Priority      : "
        f"{priority['priority']}"
    )

    print(
        f"Confidence    : "
        f"{priority['confidence']}"
    )

    print(
        f"Reason        : "
        f"{priority['reason']}"
    )

    print("\nASSIGNMENT")
    print("-" * 70)

    assignment = result["assignment"]

    print(
        f"Category      : "
        f"{assignment['recommended_category']}"
    )

    print(
        f"Subcategory   : "
        f"{assignment['recommended_subcategory']}"
    )

    print(
        f"Confidence    : "
        f"{assignment['confidence']}"
    )

    print(
        f"Reason        : "
        f"{assignment['reason']}"
    )

    print("\nRESOLUTION")
    print("-" * 70)

    resolution = result["resolution"]

    print(
        f"Mode          : "
        f"{resolution.get('mode', 'RAG')}"
    )

    print(
        f"Source Ticket : "
        f"{resolution.get('source_ticket', 'N/A')}"
    )

    print(
        f"\n{resolution['resolution']}"
    )

    print("\nSIMILAR HISTORICAL TICKETS")
    print("-" * 70)

    for ticket in result["similar_tickets"]:

        print(
            f"{ticket['ticket_id']} | "
            f"{ticket['category']} | "
            f"{ticket['subcategory']} | "
            f"{ticket['similarity_score']:.3f}"
        )

    print("\n")
    print("=" * 70)
    print("                    DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()