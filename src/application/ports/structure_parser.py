from abc import ABC, abstractmethod
import re
from typing import List, Optional
import uuid

from src.domain.entities.legal_node import LegalNode
from src.domain.enums import LegalNodeType
from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.path_builder import LegalNodePathBuilder


class LegalStructureParser(ABC):
    """Porta abstrata para parsers sintáticos de estrutura normativa."""

    @abstractmethod
    def parse_structure(self, normalized_text: str, legal_version_id: str) -> List[LegalNode]:
        """Converte texto normalizado em uma árvore de LegalNodes."""
        pass


class SyntheticLegalStructureParser(LegalStructureParser):
    """Parser determinístico simples para teste e ingestão sintética de legislação brasileira."""

    def parse_structure(self, normalized_text: str, legal_version_id: str) -> List[LegalNode]:
        if not normalized_text:
            return []

        lines = [line.strip() for line in normalized_text.split("\n") if line.strip()]
        nodes: List[LegalNode] = []

        current_art_id: Optional[str] = None
        current_par_id: Optional[str] = None

        position_counter: dict[Optional[str], int] = {}

        for line in lines:
            # Reconhecimento básico de padrões sintéticos de legislação brasileira
            if line.startswith("Art."):
                node_type = LegalNodeType.ARTIGO
                match = re.match(r"(Art\.\s*\d+[º°\.]?)", line)
                label = match.group(1) if match else "Artigo"
                identifier = label.lower().replace(".", "").replace(" ", "-").replace("º", "").replace("°", "")

                node_id = str(uuid.uuid4())
                current_art_id = node_id
                current_par_id = None
                parent_id = None

            elif line.startswith("§") or line.startswith("Parágrafo"):
                node_type = LegalNodeType.PARAGRAFO
                match = re.match(r"(§\s*\d+[º°\.]?|Parágrafo\s+único)", line, re.IGNORECASE)
                label = match.group(1) if match else "Parágrafo"
                identifier = label.lower().replace(".", "").replace(" ", "-").replace("§", "par").replace("º", "")

                node_id = str(uuid.uuid4())
                current_par_id = node_id
                parent_id = current_art_id

            elif re.match(r"^[IVXLCDM]+\s*-", line):
                node_type = LegalNodeType.INCISO
                match = re.match(r"^([IVXLCDM]+)\s*-", line)
                label = f"Inciso {match.group(1)}" if match else "Inciso"
                identifier = f"inc-{match.group(1).lower()}" if match else "inciso"

                node_id = str(uuid.uuid4())
                parent_id = current_par_id or current_art_id

            elif re.match(r"^[a-z]\)", line):
                node_type = LegalNodeType.ALINEA
                match = re.match(r"^([a-z])\)", line)
                label = f"Alínea {match.group(1)}" if match else "Alínea"
                identifier = f"ali-{match.group(1)}" if match else "alinea"

                node_id = str(uuid.uuid4())
                parent_id = current_par_id or current_art_id

            else:
                # Texto genérico ou nota
                node_type = LegalNodeType.NOTA
                label = "Nota"
                identifier = f"nota-{len(nodes)+1}"
                node_id = str(uuid.uuid4())
                parent_id = current_par_id or current_art_id

            # Incrementa contador de posição por parent_id
            pos = position_counter.get(parent_id, 0) + 1
            position_counter[parent_id] = pos

            path = LegalNodePathBuilder.build_path(identifier, parent=None)

            node = LegalNode(
                id=node_id,
                legal_version_id=legal_version_id,
                parent_id=parent_id,
                node_type=node_type,
                identifier=identifier,
                label=label,
                text=line,
                normalized_text=line,
                path=path,
                position=pos,
                content_hash=DocumentHashCalculator.calculate_sha256(line)
            )
            nodes.append(node)

        # Ajusta os paths de acordo com a hierarquia resolvida
        path_map = LegalNodePathBuilder.rebuild_all_paths(nodes)
        updated_nodes = [node.model_copy(update={"path": path_map[node.id]}) for node in nodes]

        return updated_nodes
