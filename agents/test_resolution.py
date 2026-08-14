from agents.resolution_agent import ResolutionAgent


def main():
    agent = ResolutionAgent(top_k=5)

    ticket = """
    Subject:
    Application crashes when I try to open it

    Description:
    The application crashes immediately after I open it.
    I restarted my computer but the problem still happens.
    """

    print("\nLoading agents and generating resolution...\n")

    response = agent.generate_resolution(ticket)

    print("\n" + "=" * 70)
    print("GENERATED RESOLUTION")
    print("=" * 70)
    print(response)


if __name__ == "__main__":
    main()