from abc import ABC, abstractmethod
import os
from openai import OpenAI
from google import genai
import json
from typing import Optional

# interface for LLM providers


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_json_response(self, prompt: str) -> str:
        """Generate a JSON response from the LLM."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(
            api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model

    def generate_json_response(self, prompt: str) -> str:
        """Generate a response, ensuring it's valid JSON."""
        model_instance = self.client
        response = model_instance.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=500,
                tools=[],
            ),
        )
        return response.text

    def get_model_name(self) -> str:
        return f"Gemini/{self.model}"


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_json_response(self, prompt: str) -> str:
        """Generate a response with JSON mode enabled."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()

    def get_model_name(self) -> str:
        return f"OpenAI/{self.model}"
