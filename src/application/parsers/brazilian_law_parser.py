import re
from typing import List, Tuple, Optional
import uuid
from pydantic import BaseModel

from src.application.ports.structure_parser import LegalStructureParser
from src.domain.entities.legal_node import LegalNode
from src.domain.enums import LegalNodeType
from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.normalization_service import LegalNormalizationService
from src.domain.services.path_builder import LegalPathBuilder


class ParserWarning(BaseModel):
    """Aviso estruturado gerado durante o parsing normativo (Zero Silent Data Loss)."""
    code: str = "UNSTRUCTURED_LINE"
    line_number: int
    message: str
    raw_text: str
    severity: str = "WARNING"


class BrazilianLawParser(LegalStructureParser):
    """
    PARSER ESTRUTURAL DETERMINÍSTICO DE LEGISLAÇÃO BRASILEIRA.
    Parser Versão: brazilian-law-parser@1.0.0.
    - Reconhece: NORMA, LIVRO, TÍTULO, CAPÍTULO, SEÇÃO, SUBSEÇÃO, ARTIGO, PARÁGRAFO, INCISO, ALÍNEA, ITEM, ANEXO, NOTA.
    - Suporta: Art. 1º, Art. 1., § 1º, Parágrafo único., I -, a), 1., Anexo I.
    - Preserva o RAW TEXT intacto e calcula NORMALIZED TEXT separadamente.
    - Define a raiz determinística NORMA (Sem depender de posição incidental de lista).
    - Zero Silent Data Loss: Linhas não classificadas tornam-se nós NOTA com ParserWarning estruturado.
    """

    def __init__(self, parser_version: str = "brazilian-law-parser@1.0.0"):
        self.parser_version = parser_version

    def parse_structure(
        self,
        raw_text: str,
        version_id: str
    ) -> Tuple[List[LegalNode], List[ParserWarning]]:
        nodes: List[LegalNode] = []
        warnings: List[ParserWarning] = []

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not lines:
            warnings.append(ParserWarning(
                code="EMPTY_INPUT",
                line_number=0,
                message="Texto de entrada para parsing está vazio.",
                raw_text="",
                severity="WARNING"
            ))
            return nodes, warnings

        # 1. Criação da Raiz Determinística NORMA
        title_line = lines[0]
        norma_id = f"node-norma-{version_id[:8]}"
        norma_hash = DocumentHashCalculator.calculate_canonical_node_hash("NORMA", "norma-raiz", "Ato Normativo", title_line)
        
        norma_node = LegalNode(
            id=norma_id,
            legal_version_id=version_id,
            parent_id=None,
            node_type=LegalNodeType.NORMA,
            identifier="norma-raiz",
            label="Ato Normativo",
            text=title_line,
            normalized_text=LegalNormalizationService.normalize_text(title_line),
            path="/norma",
            position=1,
            content_hash=norma_hash
        )
        nodes.append(norma_node)

        # Pilha de rastreamento de nós ancestrais
        stack: List[Tuple[int, str, str]] = [(0, norma_id, "/norma")]
        position_counter = 2

        # Padrões Regex Brasileiros
        re_livro = re.compile(r'^LIVRO\s+([MCDXLVIICLDVIX]+)', re.IGNORECASE)
        re_titulo = re.compile(r'^TÍTULO\s+([MCDXLVIICLDVIX]+)', re.IGNORECASE)
        re_capitulo = re.compile(r'^CAPÍTULO\s+([MCDXLVIICLDVIX]+)', re.IGNORECASE)
        re_secao = re.compile(r'^SEÇÃO\s+([MCDXLVIICLDVIX]+)', re.IGNORECASE)
        re_subsecao = re.compile(r'^SUBSEÇÃO\s+([MCDXLVIICLDVIX]+)', re.IGNORECASE)
        re_anexo = re.compile(r'^ANEXO\s*([MCDXLVIICLDVIX]+|\d+)?', re.IGNORECASE)
        re_artigo = re.compile(r'^(Art(?:igo|\.)?\s*(\d+[ºo°]?|\d+)\.?)', re.IGNORECASE)
        re_paragrafo_unico = re.compile(r'^Parágrafo\s+único\.?', re.IGNORECASE)
        re_paragrafo_num = re.compile(r'^§\s*(\d+[ºo°]?|\d+)\.?', re.IGNORECASE)
        re_inciso = re.compile(r'^([MCDXLVIICLDVIX]+)\s*[-–—]', re.IGNORECASE)
        re_alinea = re.compile(r'^([a-z])\)', re.IGNORECASE)
        re_item = re.compile(r'^(\d+)\.', re.IGNORECASE)

        for line in lines[1:]:
            node_type = LegalNodeType.NOTA
            identifier = f"line-{position_counter}"
            label = "Nota/Texto"
            depth = 10

            m_liv = re_livro.match(line)
            m_tit = re_titulo.match(line)
            m_cap = re_capitulo.match(line)
            m_sec = re_secao.match(line)
            m_sub = re_subsecao.match(line)
            m_ane = re_anexo.match(line)
            m_art = re_artigo.match(line)
            m_pun = re_paragrafo_unico.match(line)
            m_pnum = re_paragrafo_num.match(line)
            m_inc = re_inciso.match(line)
            m_ali = re_alinea.match(line)
            m_ite = re_item.match(line)

            if m_liv:
                node_type = LegalNodeType.LIVRO
                identifier = f"livro-{m_liv.group(1).lower()}"
                label = f"LIVRO {m_liv.group(1)}"
                depth = 1
            elif m_tit:
                node_type = LegalNodeType.TITULO
                identifier = f"titulo-{m_tit.group(1).lower()}"
                label = f"TÍTULO {m_tit.group(1)}"
                depth = 2
            elif m_cap:
                node_type = LegalNodeType.CAPITULO
                identifier = f"capitulo-{m_cap.group(1).lower()}"
                label = f"CAPÍTULO {m_cap.group(1)}"
                depth = 3
            elif m_sec:
                node_type = LegalNodeType.SECAO
                identifier = f"secao-{m_sec.group(1).lower()}"
                label = f"SEÇÃO {m_sec.group(1)}"
                depth = 4
            elif m_sub:
                node_type = LegalNodeType.SUBSECAO
                identifier = f"subsecao-{m_sub.group(1).lower()}"
                label = f"SUBSEÇÃO {m_sub.group(1)}"
                depth = 4
            elif m_ane:
                node_type = LegalNodeType.ANEXO
                num_str = (m_ane.group(1) or "1").lower()
                identifier = f"anexo-{num_str}"
                label = f"ANEXO {m_ane.group(1) or 'I'}"
                depth = 1
            elif m_art:
                node_type = LegalNodeType.ARTIGO
                num_str = re.sub(r'\D', '', m_art.group(2))
                identifier = f"art-{num_str}"
                label = f"Art. {m_art.group(2)}"
                depth = 5
            elif m_pun:
                node_type = LegalNodeType.PARAGRAFO
                identifier = "paragrafo-unico"
                label = "Parágrafo único"
                depth = 6
            elif m_pnum:
                node_type = LegalNodeType.PARAGRAFO
                num_str = re.sub(r'\D', '', m_pnum.group(1))
                identifier = f"paragrafo-{num_str}"
                label = f"§ {m_pnum.group(1)}"
                depth = 6
            elif m_inc:
                node_type = LegalNodeType.INCISO
                identifier = f"inciso-{m_inc.group(1).lower()}"
                label = f"Inciso {m_inc.group(1)}"
                depth = 7
            elif m_ali:
                node_type = LegalNodeType.ALINEA
                identifier = f"alinea-{m_ali.group(1).lower()}"
                label = f"Alínea {m_ali.group(1)}"
                depth = 8
            elif m_ite:
                node_type = LegalNodeType.ITEM
                identifier = f"item-{m_ite.group(1)}"
                label = f"Item {m_ite.group(1)}"
                depth = 9
            else:
                warnings.append(ParserWarning(
                    code="UNSTRUCTURED_LINE",
                    line_number=position_counter,
                    message=f"Linha mantida como nó NOTA (Zero Silent Data Loss): '{line[:40]}...'",
                    raw_text=line,
                    severity="WARNING"
                ))

            while stack and stack[-1][0] >= depth:
                stack.pop()

            parent_depth, parent_id, parent_path = stack[-1] if stack else (0, norma_id, "/norma")
            node_path = LegalPathBuilder.build_path(parent_path, identifier)
            node_id = f"node-{uuid.uuid4().hex[:12]}"
            
            canonical_hash = DocumentHashCalculator.calculate_canonical_node_hash(
                str(node_type), identifier, label, line
            )

            node = LegalNode(
                id=node_id,
                legal_version_id=version_id,
                parent_id=parent_id,
                node_type=node_type,
                identifier=identifier,
                label=label,
                text=line,
                normalized_text=LegalNormalizationService.normalize_text(line),
                path=node_path,
                position=position_counter,
                content_hash=canonical_hash
            )
            nodes.append(node)
            stack.append((depth, node_id, node_path))
            position_counter += 1

        return nodes, warnings
