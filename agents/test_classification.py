from agents.classification_agent import ClassificationAgent


def main():

    agent = ClassificationAgent()

    subject = "Application crashes when I try to open it"

    description = """
The application crashes immediately after I open it.
I restarted my computer but the problem still happens.
"""

    result = agent.classify(
        subject=subject,
        description=description
    )

    print("\n==============================")
    print("CLASSIFICATION AGENT")
    print("==============================")
    print(f"Category: {result['category']}")
    print(f"Subcategory: {result['subcategory']}")
    print(f"Confidence: {result['confidence']}")


if __name__ == "__main__":
    main()