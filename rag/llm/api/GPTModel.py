import os

from dotenv import load_dotenv
from openai import OpenAI


class GPTModel:
    load_dotenv()

    def __init__(self, model_name: str, price_per_token_input: float, price_per_token_output: float):
        self.response = None
        self.client = self._initialize_opeanai()
        self._model_name = model_name
        self.price_per_token_input = price_per_token_input
        self.price_per_token_output = price_per_token_output

    @staticmethod
    def _initialize_opeanai():
        return OpenAI(api_key=os.getenv("OPENAI_APIKEY"))

    def generate_completion(self, prompt: list) -> str:
        self.response = self._generate_response(prompt)
        return self._get_completion(self.response)

    def _generate_response(self, prompt: list):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            temperature=0.1,
        )

    @staticmethod
    def _get_completion(response) -> str:
        return response.choices[0].message.content

    @property
    def model_name(self):
        return self._model_name

    @property
    def cost(self):
        prompt_cost = self.response.usage.prompt_tokens * self.price_per_token_input
        output_cost = self.response.usage.completion_tokens * self.price_per_token_input
        return prompt_cost + output_cost

    @cost.setter
    def cost(self, value):
        pass
