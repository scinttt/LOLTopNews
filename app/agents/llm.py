import os
from langchain.chat_models import init_chat_model
from agents.tools import websearch


def extractor_llm(temperature: float = 0.7, bind_tools: bool = False):
    """创建 LLM 实例，可选绑定工具"""
    
    llm = init_chat_model("deepseek-chat", temperature=temperature)

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm

def analyzer_llm(temperature: float = 0.7, bind_tools: bool = True):
    """创建 LLM 实例，可选绑定工具"""
    
    llm = init_chat_model("deepseek-chat", temperature=temperature)

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm

def summarizer_llm(temperature: float = 0.7, bind_tools: bool = False):
    """创建 LLM 实例，可选绑定工具"""
    
    llm = init_chat_model(
        "gpt-4o", 
        temperature=temperature,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    if bind_tools:
        llm = llm.bind_tools([websearch])

    return llm
