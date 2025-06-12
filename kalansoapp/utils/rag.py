
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
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


def rag_with_qa(persist_path, llm, prompt):
    vectordb= Chroma(persist_directory=persist_path, embedding_function=EMBEDDING_MODEL)
    #retriever = vectordb.as_retriever()
    docs = vectordb.similarity_search(query="analyse pédagogique", k=8)
    context = " ".join([doc.page_content for doc in docs])
    final_prompt = prompt.format(context = context)
    response = llm.invoke(final_prompt).content
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm= llm,
    #     return_source_documents = True,
       
    # )
    # response = qa_chain.invoke(prompt)
    return response


# RAG pipeline
def rag_answer(question, persist_path, llm):
    vectorstore = load_vectorstore(persist_path)
    retrieved_docs = vectorstore.similarity_search(question, k=8)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    full_prompt = PROMPT.format(context=context, question=question)
    
    response = eval(llm.invoke(full_prompt).content)  # ou json.loads(...) si tu modifies le prompt

    return response


from langchain_openai import AzureChatOpenAI
# Azure LLM config
llm = AzureChatOpenAI(
    openai_api_version="2024-07-01-preview",
    deployment_name="gpt-35-turbo-chefquiz",
    openai_api_key="h5R1YOBt2Q5WU56488stKWc7GiO9nEG3Z344ITLK3mTb6uGkdlKLJQQJ99BAACYeBjFXJ3w3AAABACOGLM5j",
    openai_api_type="azure",
    azure_endpoint="https://realtimekokou.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
)


# persist_path = "./../../media/chroma/Cloud1221_1"
# from .prompt import feedback_prompt
# resutlt = rag_with_qa(persist_path, llm, feedback_prompt)
# print(resutlt)