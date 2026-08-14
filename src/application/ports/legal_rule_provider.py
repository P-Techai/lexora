from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule


class LegalRuleProvider(ABC):
    """
    Porta abstrata de aplicação para prover regras fiscais fundamentadas e evidências do Legal Brain.
    O Fiscal Brain NÃO acessa o banco relacional/jurídico diretamente.
    """

    @abstractmethod
    async def get_applicable_legal_rules(self, fact: FiscalFact, reference_date: date) -> List[FiscalTaxRule]:
        """Recupera regras fiscais aplicáveis com base nos fatos e data de referência."""
        pass

    @abstractmethod
    async def get_legal_evidence(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Recupera metadados de evidência jurídica vinculada à regra fiscal."""
        pass

    @abstractmethod
    async def get_normative_basis(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Recupera os detalhes do dispositivo legal (LegalNode/Version) fundamentando a regra."""
        pass
