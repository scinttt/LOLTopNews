import os

from agents.tools import websearch
from langchain_openai import ChatOpenAI

# AI Builders Space unified API
_BASE_URL = os.getenv("AI_BUILDER_BASE_URL", "https://space.ai-builders.com/backend/v1")
_API_KEY = os.getenv("AI_BUILDER_TOKEN", "")


def _create_llm(model: str, temperature: float, **kwargs) -> ChatOpenAI:
    """Create a ChatOpenAI instance pointing at AI Builders Space."""
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=_BASE_URL,
        api_key=_API_KEY,
        **kwargs,
    )


def extractor_llm(temperature: float = 0.7, bind_tools: bool = False):
    """Create LLM for the extractor node."""
    llm = _create_llm("deepseek", temperature=temperature)

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm


def analyzer_llm(temperature: float = 0.7, bind_tools: bool = True):
    """Create LLM for the analyzer node."""
    llm = _create_llm("deepseek", temperature=temperature)

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm


def summarizer_llm(temperature: float = 0.7, bind_tools: bool = False):
    """Create LLM for the summarizer node."""
    llm = _create_llm("deepseek", temperature=temperature)

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm
