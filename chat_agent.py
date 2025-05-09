# chat_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
# from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import GoogleGenerativeAIEmbeddings


import os

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Optional: Create a memory for conversational context
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Prompt template
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful AI assistant. Use the following context to answer the question.
If the answer is not in the context, say "I don't have enough information."

Context: {context}
Question: {question}
""",
)

def load_vectorstore():
    if os.path.exists("faiss_index"):
        return FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
    else:
        return None

def create_vectorstore_from_texts(texts: list[str]):
    docs = [Document(page_content=t) for t in texts]
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    vectorstore.save_local("faiss_index")
    return vectorstore

def chat_with_agent(query, mode="chat", history=None):
    if mode == "search":
        vectorstore = load_vectorstore()
        if not vectorstore:
            return [{"source": "System", "snippet": "❌ Vector store not found. Please initialize it."}]
        
        retriever = vectorstore.as_retriever()
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": QA_PROMPT}
        )
        answer = qa.run(query)
        return [{"source": "Gemini + Vectorstore", "snippet": answer}]
    
    # Default mode: simple chat
    if history is None:
        history = []
    context = "\n".join([f"{h[0]}: {h[1]}" for h in history])
    prompt = f"{context}\nUser: {query}\nAI:"
    response = llm.invoke(prompt)
    return response.content


from chat_agent import create_vectorstore_from_texts
from news_aggregator import get_latest_news

news_items = get_latest_news()
news_texts = [n["title"] + "\n" + (n["content"] or "") for n in news_items]
create_vectorstore_from_texts(news_texts)
