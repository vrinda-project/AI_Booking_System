from langchain_community.embeddings import OpenAIEmbeddings
from typing import List
from ..config import settings

class EmbeddingManager:
    """Manage embeddings for RAG system"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for query"""
        return self.embeddings.embed_query(query)