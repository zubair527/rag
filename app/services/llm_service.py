"""LLM service using Ollama with LangChain"""
from typing import List, Dict, Any, Optional
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """Service for LLM interactions using LangChain"""

    def __init__(self):
        self.llm: Optional[Ollama] = None
        self.qa_chain = None

    def initialize(self) -> None:
        """Initialize LLM and chains"""
        logger.info(f"Initializing Ollama LLM: {settings.ollama_model}")

        self.llm = Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.ollama_temperature,
        )

        # Create QA prompt template
        qa_template = """You are a helpful AI assistant answering questions based on the provided context.
Use the following pieces of context to answer the question at the end.
If you don't know the answer or the context doesn't contain relevant information, just say that you don't know, don't try to make up an answer.
Always provide a clear and concise answer.

Context:
{context}

Question: {question}

Answer:"""

        self.qa_prompt = ChatPromptTemplate.from_template(qa_template)

        # Create the QA chain
        self.qa_chain = (
            {
                "context": lambda x: x["context"],
                "question": lambda x: x["question"]
            }
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info("LLM service initialized successfully")

    def generate_answer(
        self,
        question: str,
        context: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate answer using context"""
        if not self.qa_chain:
            raise RuntimeError("LLM service not initialized")

        # Update LLM parameters if provided
        if temperature is not None:
            self.llm.temperature = temperature
        if max_tokens is not None:
            self.llm.num_predict = max_tokens

        try:
            # Generate answer
            answer = self.qa_chain.invoke({
                "question": question,
                "context": context
            })

            return answer.strip()

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise RuntimeError(f"Failed to generate answer: {str(e)}")

    def format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context string"""
        context_parts = []

        for idx, result in enumerate(search_results, 1):
            content = result.get("content", "")
            filename = result.get("filename", "Unknown")
            chunk_index = result.get("chunk_index", 0)

            context_part = f"[Source {idx} - {filename} (chunk {chunk_index})]:\n{content}"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def get_model_name(self) -> str:
        """Get current model name"""
        return settings.ollama_model


# Global LLM service instance
llm_service = LLMService()
