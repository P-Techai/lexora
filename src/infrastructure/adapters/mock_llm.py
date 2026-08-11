from typing import Any, Dict, Optional

from src.application.ports.llm_provider import LLMProvider


class MockLLMAdapter(LLMProvider):
    """Adaptador mock para simulação de invocação de LLMs em ambiente de teste isolado."""

    def __init__(self, default_response: str = "Resposta mock de teste do LÉXORA."):
        self.default_response = default_response

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[MOCK_LLM]: {self.default_response} (Prompt: {prompt[:30]}...)"

    async def extract_structured_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            "status": "MOCK_EXTRACTION_SUCCESS",
            "extracted_data": {},
            "prompt_snippet": prompt[:50]
        }
