from langchain_community.document_loaders import PyPDFLoader

def load_pdf_documents(filepath: str):
    loader = PyPDFLoader(filepath)
    return loader.load()
