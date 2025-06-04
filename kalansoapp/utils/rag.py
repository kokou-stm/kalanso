
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain.prompts import PromptTemplate
import os
import torch

# Embedding model et prompt statiques
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""Tu es un expert en domaine. Utilise les informations suivantes pour répondre à la question.

Contexte : {context}

Question : {question}

Réponse :
"""
)


# Créer ou charger la base vectorielle
def create_vectorstore(documents, persist_path):
    return Chroma.from_documents(documents, EMBEDDING_MODEL, persist_directory=persist_path)

def load_vectorstore(persist_path):
    return Chroma(persist_directory=persist_path, embedding_function=EMBEDDING_MODEL)

# RAG pipeline
def rag_answer(question, persist_path, llm):
    vectorstore = load_vectorstore(persist_path)
    retrieved_docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    full_prompt = PROMPT.format(context=context, question=question)
    
    response = eval(llm.invoke(full_prompt).content)  # ou json.loads(...) si tu modifies le prompt

    return response
