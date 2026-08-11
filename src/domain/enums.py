from enum import Enum


class LegalNodeType(str, Enum):
    NORMA = "NORMA"
    LIVRO = "LIVRO"
    TITULO = "TITULO"
    CAPITULO = "CAPITULO"
    SECAO = "SECAO"
    SUBSECAO = "SUBSECAO"
    ARTIGO = "ARTIGO"
    PARAGRAFO = "PARAGRAFO"
    INCISO = "INCISO"
    ALINEA = "ALINEA"
    ITEM = "ITEM"
    NOTA = "NOTA"


class LegalRelationType(str, Enum):
    AMENDS = "AMENDS"
    REVOKES = "REVOKES"
    REGULATES = "REGULATES"
    REFERENCES = "REFERENCES"
    COMPLEMENTS = "COMPLEMENTS"
    SUPERSEDES = "SUPERSEDES"
    RATIFIES = "RATIFIES"
    SUSPENDS = "SUSPENDS"


class TaxRegime(str, Enum):
    SIMPLES_NACIONAL = "SIMPLES_NACIONAL"
    LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO"
    LUCRO_REAL = "LUCRO_REAL"
    MEI = "MEI"


class TaxType(str, Enum):
    ICMS = "ICMS"
    ICMS_ST = "ICMS_ST"
    DIFAL = "DIFAL"
    PIS = "PIS"
    COFINS = "COFINS"
    ISS = "ISS"
    IPI = "IPI"
    CBS = "CBS"
    IBS = "IBS"
    IS = "IS"


class NodeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"
    DRAFT = "DRAFT"
