from utils.config import get_settings

def get_llm():
    """Return configured LLM based on settings — same factory pattern as embedder_factory"""
    settings = get_settings()

    if settings.LLM_PROVIDER == "openai":
        from llm.openai_llm import OpenAILLM
        return OpenAILLM()
    elif settings.LLM_PROVIDER == "gemini":
        from llm.gemini_llm import GeminiLLM
        return GeminiLLM()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")