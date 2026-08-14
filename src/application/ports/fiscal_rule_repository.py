from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.enums import TaxType
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule


class FiscalTaxRuleRepository(ABC):
    """
    Porta de repositório para persistência e consulta de regras tributárias formais.
    """

    @abstractmethod
    async def save_rule(self, rule: FiscalTaxRule) -> FiscalTaxRule:
        """Persiste ou atualiza uma regra fiscal."""
        pass

    @abstractmethod
    async def get_rule_by_id(self, rule_id: str) -> Optional[FiscalTaxRule]:
        """Obtém regra pelo ID."""
        pass

    @abstractmethod
    async def get_active_rules_by_tax_type(self, tax_type: TaxType, reference_date: date) -> List[FiscalTaxRule]:
        """Obtém regras ativas para um tributo na data de referência."""
        pass

    @abstractmethod
    async def list_all_active_rules(self, reference_date: date) -> List[FiscalTaxRule]:
        """Obtém todas as regras ativas na data de referência."""
        pass
