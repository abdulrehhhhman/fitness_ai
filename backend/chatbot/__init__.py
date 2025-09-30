
"""
Chatbot Module

This module provides an AI-powered fitness coach chatbot using Groq API
and Retrieval-Augmented Generation (RAG) for enhanced responses.

Features:
- Natural language conversation interface
- Fitness and nutrition expertise
- RAG-based knowledge retrieval
- Motivational coaching style
- Context-aware responses

Powered by:
- Groq API (Llama 3.1 8B model)
- Sentence Transformers for embeddings
- FAISS for similarity search
"""

from .service import chatbot_service
from .routes import router
from .schemas import ChatRequest, ChatResponse

__all__ = [
    "chatbot_service",
    "router",
    "ChatRequest",
    "ChatResponse"
]