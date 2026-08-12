import ipaddress
from urllib.parse import urlparse
from typing import List, Optional

from src.domain.exceptions import SSRFProtectionError, UrlNotAllowedError


class URLSecurityValidator:
    """Validador de segurança de URLs e proteção estrita contra SSRF (Server-Side Request Forgery)."""

    BLOCKED_HOSTNAMES = {"localhost", "loopback", "0.0.0.0"}
    METADATA_IP = "169.254.169.254"

    @classmethod
    def validate_url(cls, url: str, allowed_domains: Optional[List[str]] = None) -> str:
        """
        Valida o esquema, o domínio da allowlist e bloqueia vetores de ataque SSRF.
        Lança SSRFProtectionError ou UrlNotAllowedError se inválida.
        """
        if not url or not isinstance(url, str):
            raise UrlNotAllowedError("URL inválida ou vazia.")

        parsed = urlparse(url.strip())

        # 1. Esquema permitido: HTTP ou HTTPS
        if parsed.scheme.lower() not in ("http", "https"):
            raise UrlNotAllowedError(f"Esquema de URL '{parsed.scheme}' não é permitido. Apenas HTTP/HTTPS são aceitos.")

        hostname = parsed.hostname
        if not hostname:
            raise UrlNotAllowedError("URL não contém um nome de host (hostname) válido.")

        hostname_lower = hostname.lower()

        # 2. Bloqueio de Hostnames Reservados / Localhost
        if hostname_lower in cls.BLOCKED_HOSTNAMES or hostname_lower.endswith(".localhost"):
            raise SSRFProtectionError(f"Acesso a hostnames locais ('{hostname}') é estritamente proibido (Proteção SSRF).")

        # 3. Bloqueio de Endereços IP Privados e Metadata Endpoints
        try:
            ip = ipaddress.ip_address(hostname_lower)
            if ip.is_loopback:
                raise SSRFProtectionError("Acesso a endereços IP de loopback é proibido (Proteção SSRF).")
            if ip.is_private:
                raise SSRFProtectionError(f"Acesso a subredes IP privadas ('{ip}') é proibido (Proteção SSRF).")
            if str(ip) == cls.METADATA_IP:
                raise SSRFProtectionError("Acesso a endpoints de metadados de nuvem é proibido (Proteção SSRF).")
            if ip.is_reserved or ip.is_link_local:
                raise SSRFProtectionError(f"Acesso a endereços IP reservados/link-local ('{ip}') é proibido (Proteção SSRF).")
        except ValueError:
            # Não é um endereço IP numérico, é um nome de domínio regular
            pass

        # 4. Validação da Allowlist de Domínios (se fornecida)
        if allowed_domains is not None:
            domain_matched = False
            for allowed in allowed_domains:
                allowed_clean = allowed.lower().strip()
                if hostname_lower == allowed_clean or hostname_lower.endswith(f".{allowed_clean}"):
                    domain_matched = True
                    break

            if not domain_matched:
                raise UrlNotAllowedError(
                    f"O domínio '{hostname}' não pertence à lista de domínios autorizados da fonte: {allowed_domains}."
                )

        return url.strip()
