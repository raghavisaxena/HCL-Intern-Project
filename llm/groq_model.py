import os
from groq import Groq
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class GroqModel:

    def __init__(self, model_name: str = "openai/gpt-oss-120b"):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Check your .env file."
            )

        logger.info(f"Initializing Groq model: {model_name}")

        self.client = Groq(api_key=api_key)
        self.model_name = model_name

        logger.info("Groq model ready.")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 40
    ):

        response = self.client.chat.completions.create(
    model=self.model_name,
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=max_new_tokens,
    temperature=0,
    reasoning_effort="low"
)

        return response.choices[0].message.content.strip()