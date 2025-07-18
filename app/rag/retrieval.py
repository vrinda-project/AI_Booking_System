from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from ..config import settings

class RetrievalChain:
    """Retrieval chain for RAG system"""
    
    def __init__(self, vectorstore: Chroma):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key
        )
        
        self.retrieval_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
    
    def query(self, question: str) -> str:
        """Query the retrieval chain"""
        return self.retrieval_chain.run(question)