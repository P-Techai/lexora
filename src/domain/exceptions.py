class LexoraDomainError(Exception):
    """Exceção base para erros do domínio da aplicação LÉXORA."""
    pass


class InvalidLegalDocumentError(LexoraDomainError):
    """Lançada quando um documento jurídico possui campos obrigatórios inválidos ou ausentes."""
    pass


class InvalidEffectivePeriodError(LexoraDomainError):
    """Lançada quando o período de vigência é inconsistente (ex.: effective_until < effective_from)."""
    pass


class InvalidLegalNodeError(LexoraDomainError):
    """Lançada quando um dispositivo normativo possui estrutura ou tipo inválidos."""
    pass


class DuplicateLegalDocumentError(LexoraDomainError):
    """Lançada ao tentar ingerir um documento com hash idêntico já cadastrado sem nova versão."""
    pass


class MissingEvidenceError(LexoraDomainError):
    """Lançada quando uma relação jurídica exige evidência que não foi fornecida."""
    pass


class MissingRevokingSourceError(LexoraDomainError):
    """Lançada quando tenta-se criar uma relação de revogação sem fornecer um nó/ato revogador distinto."""
    pass


class TreeCycleDetectedError(LexoraDomainError):
    """Lançada quando um nó hierárquico aponta para um ancestral gerando um ciclo na árvore."""
    pass


class InconsistentPositionError(LexoraDomainError):
    """Lançada quando nós no mesmo nível hierárquico possuem posições duplicadas ou inconsistentes."""
    pass


# --- Exceções de Aquisição e Segurança ---

class SourceNotAllowedError(LexoraDomainError):
    """Lançada quando tenta-se adquirir de uma fonte inativa ou não permitida."""
    pass


class UrlNotAllowedError(LexoraDomainError):
    """Lançada quando uma URL não pertence ao domínio permitido da fonte."""
    pass


class SSRFProtectionError(LexoraDomainError):
    """Lançada quando uma URL aponta para IPs privados, localhost ou endpoints de metadados."""
    pass


class AcquisitionTimeoutError(LexoraDomainError):
    """Lançada quando uma requisição de aquisição ultrapassa o tempo limite configurado."""
    pass


class UnsupportedContentTypeError(LexoraDomainError):
    """Lançada quando o servidor de origem retorna um tipo de conteúdo (MIME) não suportado."""
    pass


class ArtifactTooLargeError(LexoraDomainError):
    """Lançada quando o artefato bruto ultrapassa o tamanho máximo em bytes permitido."""
    pass


class AcquisitionFailedError(LexoraDomainError):
    """Lançada quando ocorre uma falha de conexão HTTP ou erro 4xx/5xx de servidor."""
    pass


class RedirectNotAllowedError(LexoraDomainError):
    """Lançada quando um redirecionamento HTTP aponta para um domínio não autorizado."""
    pass


class ConfigurationError(LexoraDomainError):
    """Lançada quando há erro de configuração de ambiente ou provedor de produção desconfigurado."""
    pass


# --- Exceções de Contextual Legal RAG e Guardrails ---

class LegalAnswerGenerationError(LexoraDomainError):
    """Lançada quando ocorre uma falha na geração textual de resposta jurídica pelo gerador."""
    pass


class LegalAnswerValidationError(LexoraDomainError):
    """Lançada quando a resposta gerada viola os guardrails jurídicos de validação."""
    pass


class CitationValidationError(LexoraDomainError):
    """Lançada quando a resposta contém citação inventada, inexistente ou temporalmente inválida."""
    pass


class ProvenanceValidationError(LexoraDomainError):
    """Lançada quando uma citação ou evidência possui a cadeia de proveniência em 5 níveis incompleta."""
    pass


class TemporalAnswerError(LexoraDomainError):
    """Lançada quando a resposta utiliza um dispositivo fora da data de referência solicitada."""
    pass


class ContextBudgetExceededError(LexoraDomainError):
    """Lançada quando a montagem do contexto excede o orçamento de caracteres/tokens permitido."""
    pass
