from agents.priority_agent import PriorityAgent


def main():

    agent = PriorityAgent()

    subject = "Application crashes when I try to open it"

    description = """
The application crashes immediately after I open it.
I restarted my computer but the problem still happens.
"""

    result = agent.determine_priority(
        subject=subject,
        description=description
    )

    print("\n==============================")
    print("PRIORITY AGENT")
    print("==============================")
    print(f"Priority: {result['priority']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reason: {result['reason']}")


if __name__ == "__main__":
    main()