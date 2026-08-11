from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """Porta abstrata para modelos de linguagem (OpenAI, Gemini, Anthropic, Cloudflare Workers AI)."""

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Gera resposta em texto simples a partir de um prompt."""
        pass

    @abstractmethod
    async def extract_structured_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extrai dados estruturados em JSON validados contra um schema especificado."""
        pass
