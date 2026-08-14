import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from loguru import logger

from llm.config import MODEL_NAME


class Phi3Model:

    def __init__(self):
        logger.info(f"Loading model: {MODEL_NAME}")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="cpu"
        )

        self.model.eval()

        logger.info("Phi-3 Mini loaded successfully.")

    def generate(self, prompt: str, max_new_tokens: int = 200):

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.2,
                do_sample=True
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

        response = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        )

        return response.strip()