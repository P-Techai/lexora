from typing import Dict, List, Optional

from src.application.ports.repositories import SourceRepository
from src.domain.entities.source import Source
from src.domain.enums import Jurisdiction, SourcePolicy
from src.domain.exceptions import SourceNotAllowedError


class SourceRegistryService:
    """Serviço de Registro e Governança de Fontes da aplicação LÉXORA."""

    def __init__(self, source_repo: SourceRepository):
        self.source_repo = source_repo
        # Mapeamento em memória de domínios permitidos por fonte (Source -> Allowed Domains)
        self._allowed_domains_map: Dict[str, List[str]] = {}
        self._source_policies_map: Dict[str, SourcePolicy] = {}

    def register_source_policy(
        self,
        source_id: str,
        policy: SourcePolicy,
        allowed_domains: List[str]
    ) -> None:
        """Registra a política de segurança e a lista de domínios permitidos para a fonte."""
        self._source_policies_map[source_id] = policy
        self._allowed_domains_map[source_id] = [d.lower().strip() for d in allowed_domains]

    def get_allowed_domains(self, source_id: str) -> List[str]:
        return self._allowed_domains_map.get(source_id, [])

    def get_policy(self, source_id: str) -> SourcePolicy:
        return self._source_policies_map.get(source_id, SourcePolicy.UNTRUSTED)

    async def validate_source_active_and_policy(self, source_id: str) -> Source:
        """Valida se a fonte existe, está ativa e autorizada para aquisição."""
        source = await self.source_repo.get_by_id(source_id)
        if not source:
            raise SourceNotAllowedError(f"Fonte com ID '{source_id}' não está cadastrada no repositório.")
        if not source.active:
            raise SourceNotAllowedError(f"Fonte '{source.name}' (ID: {source_id}) está inativa.")

        policy = self.get_policy(source_id)
        if policy == SourcePolicy.UNTRUSTED:
            raise SourceNotAllowedError(f"Fonte '{source.name}' possui política UNTRUSTED e não permite aquisições.")

        return source
