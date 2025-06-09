import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os

class HuggingFaceModel:
    def __init__(self, model_name: str, use_4bit: bool = True):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=use_4bit,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        ) if use_4bit else None

        self._load_model_and_tokenizer()

    def _load_model_and_tokenizer(self):

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            quantization_config=self.bnb_config,
            token=os.getenv("HUGGINGFACE_TOKEN")
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            use_fast=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

    def infer(self, messages: list[dict], max_new_tokens: int = 1024, temperature: float = 0.2) -> str:
        prompt_text = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False
        )

        inputs = self.tokenizer(
            prompt_text,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            use_cache=True,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(inputs["input_ids"], outputs)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return response
