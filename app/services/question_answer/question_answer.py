from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnableWithMessageHistory

from app.core.config.llm import LLMService
from app.genai.services.question_answer.memory import SessionManager
from app.core.config.vector_store import VectorStoreService
from app.core.config.embeddings import EmbeddingService
from app.core.config.config import settings


class QuestionAnswerService:
    def __init__(self, post_id: str, user_id: str, question: str, post_content: str):
        self.post_id = post_id
        self.user_id = user_id
        self.question = question
        self.post_content = post_content
        self.session_manager = SessionManager()

        embedder = EmbeddingService(model=settings.HUGGINGFACE_EMBEDDING_MODEL, api_key=settings.HUGGINGFACE_API_KEY)
        self.vector_store_service = VectorStoreService(
            connection_string=settings.SQLALCHEMY_DATABASE_URI,
            embedding_service=embedder,
        )

        self.vector_store_service.store_blog_post(blog_post_id=post_id, content=self.post_content)
        self.llm_service = LLMService(temperature=0.3)

    

    def get_retriever(self):
        retriever = self.vector_store_service.get_retriever(self.post_id)
        return retriever
    
    def create_contextualize_q_prompt(self):
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return contextualize_q_prompt
    
    def create_qa_prompt(self):
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return qa_prompt
    

    def create_chains(self, retriever):
        contextualize_q_prompt = self.create_contextualize_q_prompt()
        history_aware_retriever = create_history_aware_retriever(
            self.llm_service.llm, retriever, contextualize_q_prompt
        )

        qa_prompt = self.create_qa_prompt()
        question_answer_chain = create_stuff_documents_chain(self.llm_service.llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return rag_chain

    def create_conversational_rag_chain(self):
        rag_chain = self.create_chains(self.get_retriever())
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.session_manager.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        return conversational_rag_chain
    
    def get_answer(self, question: str):
        try:
            conversational_rag_chain = self.create_conversational_rag_chain()
            answer = conversational_rag_chain.invoke(
                {"input": question},
                config={
                    "configurable": {"session_id": self.user_id}
                },
            )["answer"]
            return str(answer)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
       
if __name__ == "__main__":

    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

    # Initialize the service
    user_id = "abc123"
    post_id = "123abc"
    post_content = "This is a blog post about AI in healthcare."
    question = "What is AI used for in healthcare?"
    service = QuestionAnswerService(user_id=user_id, post_id=post_id, post_content=post_content, question=question)
    print(f"Service initialized with post_id: {service.post_id}, question: {service.question}")

    conversational_rag_chain = service.create_conversational_rag_chain()
    print("Conversational RAG chain created")
    conversational_rag_chain.invoke(
        {"input": "What is AI used for in healthcare?"},
        config={
            "configurable": {"session_id": user_id}
        },  # constructs a key "abc123" in `store`.
        )["answer"]
    print(service.session_manager.store)

    service2 = QuestionAnswerService(user_id="foo", post_id=post_id, post_content=post_content, question="What is AI used for in logistics?")
    print(f"Service initialized with post_id: {service.post_id}, question: {service.question}")

    conversational_rag_chain = service2.create_conversational_rag_chain()
    print("Conversational RAG chain created")
    conversational_rag_chain.invoke(
        {"input": "What is AI used for in healthcare?"},
        config={
            "configurable": {"session_id": "foo"}
        },  # constructs a key "abc123" in `store`.
        )["answer"]
    print(service2.session_manager.store)

    


