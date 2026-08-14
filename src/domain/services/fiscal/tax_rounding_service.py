from decimal import Decimal, ROUND_HALF_UP


class TaxRoundingService:
    """
    Serviço determinístico de arredondamento tributário com precisão Decimal.
    NUNCA utiliza float.
    """

    @staticmethod
    def round_amount(value: Decimal, scale: int = 2) -> Decimal:
        """
        Arredonda um valor Decimal para a escala especificada (padrão 2 casas decimais)
        utilizando a estratégia padrão de arredondamento tributário (ROUND_HALF_UP).
        """
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        quantizer = Decimal("10") ** (-scale)
        return value.quantize(quantizer, rounding=ROUND_HALF_UP)

    @staticmethod
    def round_rate(rate: Decimal, scale: int = 4) -> Decimal:
        """
        Arredonda uma alíquota Decimal (ex.: 18.0000%).
        """
        if not isinstance(rate, Decimal):
            rate = Decimal(str(rate))

        quantizer = Decimal("10") ** (-scale)
        return rate.quantize(quantizer, rounding=ROUND_HALF_UP)
