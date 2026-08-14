from llm.phi_model import Phi3Model


def main():

    model = Phi3Model()

    prompt = """
You are an IT support assistant.

Analyze this IT support ticket:

Subject:
Application crashes when I try to open it

Description:
The application crashes immediately after I open it.
I restarted my computer but the problem still happens.

Give:
1. Category
2. Priority
3. Short explanation
"""

    response = model.generate(prompt)

    print("\n==============================")
    print("PHI-3 MINI RESPONSE")
    print("==============================")
    print(response)


if __name__ == "__main__":
    main()