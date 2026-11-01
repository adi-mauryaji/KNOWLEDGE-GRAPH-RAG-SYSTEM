from retrieval.hybrid_retriever import HybridRetriever
from llm.llm_factory import get_llm
from services.citation_service import CitationService
from models.chat import Citation
from llm.prompt_templates import RAG_SYSTEM_PROMPT, RAG_USER_TEMPLATE

class ChatService:

    def __init__(self):
        self.retriever = HybridRetriever()
        self.llm = get_llm()
        self.citation_service = CitationService()

    async def answer_query(
        self, query: str, doc_ids: list[str] = None, top_k: int = 5
    ) -> tuple[str, list[Citation]]:

        # Step 1: Hybrid retrieval
        context, retrieved_chunks = await self.retriever.retrieve(
            query=query, top_k=top_k, doc_ids=doc_ids
        )

        if not retrieved_chunks:
            return "I couldn't find relevant information in the uploaded documents.", []

        # Step 2: Build prompt
        prompt = RAG_USER_TEMPLATE.format(context=context, query=query)

        # Step 3: LLM call
        raw_answer = await self.llm.complete(system=RAG_SYSTEM_PROMPT, user=prompt)

        # Step 4: Extract citations from answer
        citations = self.citation_service.extract_citations(
            answer=raw_answer, retrieved_chunks=retrieved_chunks
        )

        return raw_answer, citations