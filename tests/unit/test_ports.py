import pytest
from src.infrastructure.adapters.local_storage import LocalStorageAdapter
from src.infrastructure.adapters.mock_llm import MockLLMAdapter


@pytest.mark.asyncio
async def test_local_storage_adapter(tmp_path):
    storage = LocalStorageAdapter(base_path=str(tmp_path))
    key = "test_doc.xml"
    data = b"<nfeProc><NFe>XML de Teste</NFe></nfeProc>"

    saved_path = await storage.save_bytes(key, data)
    assert saved_path is not None

    retrieved = await storage.get_bytes(key)
    assert retrieved == data

    deleted = await storage.delete(key)
    assert deleted is True
    assert await storage.get_bytes(key) is None


@pytest.mark.asyncio
async def test_mock_llm_adapter():
    llm = MockLLMAdapter()
    text_response = await llm.generate_text("Qual o conceito de insumo para PIS/COFINS?")
    assert "[MOCK_LLM]" in text_response

    json_response = await llm.extract_structured_json("Extrair artigo", schema={})
    assert json_response["status"] == "MOCK_EXTRACTION_SUCCESS"
