from langchain_community.document_loaders import UnstructuredPDFLoader
import os
import nltk
import time

tiempo_inicial = time.time()

# Obtener el directorio actual
current_dir = os.getcwd()
print(f"Estás en: {current_dir}")

# Ruta del archivo PDF
doc_path = "/home/daniel/Documents/docker/volumes/scipy_notebook/term3/BigDataCapstoneProject/codes/ollamaTest/pdf_rag/data/resume.pdf"
model = "llama3.2"

# Verificar si el PDF existe
if not os.path.exists(doc_path):
    print(f"Error: El archivo {doc_path} no existe.")
    exit()

# Cargar el PDF
loader = UnstructuredPDFLoader(file_path=doc_path)
data = loader.load()
print("done loading ...")

# Verificar si se extrajo contenido
if data:
    content = data[0].page_content
else:
    print("Error: No se pudo extraer contenido del PDF.")
    exit()

# Dividir el texto en fragmentos pequeños
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
chunks = text_splitter.split_documents(data)
print("done splitting")

# Descargar modelo de embeddings
import ollama
try:
    ollama.pull("nomic-embed-text")
except Exception as e:
    print(f"Error descargando modelo: {e}")

# Crear base de datos de vectores
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="simple-rag"
)

print("done adding to vector database ...")

# Configurar LLM para recuperación de información
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

llm = ChatOllama(model=model)

QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are a hiring manager and your task is to answer questions about the candidate: {question}"""
)

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(),
    llm,
    prompt=QUERY_PROMPT
)

# Definir plantilla de RAG
template = """Answer the question based only on the following context: {context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# Definir pipeline de recuperación y generación
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Realizar consulta
res = chain.invoke({"question": "What are the soft skills of the candidate"})
print(res)
print("next question")
res = chain.invoke({"question": "What are the tecnical skills of the candidate"})
print(res)

tiempo_final = time.time() - tiempo_inicial
print("El modelo demoro: ", tiempo_final)