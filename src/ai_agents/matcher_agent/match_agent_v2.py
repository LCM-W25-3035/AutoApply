from langchain_community.document_loaders import UnstructuredPDFLoader
import os
import time
import pandas as pd
import numpy as np
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from sklearn.metrics.pairwise import cosine_similarity

# Medir tiempo de ejecución
tiempo_inicial = time.perf_counter()

# Obtener el directorio actual
current_dir = os.getcwd()
print(f"Estás en: {current_dir}")

# Ruta de archivos
doc_path_resume = "./pdf_rag/data_resume/resume.pdf"
doc_path_jobs = "./pdf_rag/data_jobs/job_dataset.csv"
model = "llama3.2"

# Cargar dataset de ofertas de trabajo
df_jobs = pd.read_csv(doc_path_jobs)

# Verificar si la columna existe
if "Job Description" not in df_jobs.columns:
    print("Error: El archivo CSV no contiene la columna 'Job Description'.")
    exit()

# Eliminar filas con valores NaN y limpiar texto
df_jobs = df_jobs.dropna(subset=["Job Description"])
df_jobs["Job Description"] = df_jobs["Job Description"].astype(str).str.strip()
df_jobs = df_jobs[df_jobs["Job Description"] != ""]  # Eliminar filas vacías

# Seleccionar primeras 11 ofertas de trabajo
job_descriptions = df_jobs["Job Description"].tolist()[:11]

# Depuración: Verificar contenido antes de procesar
print(f"Cantidad de job descriptions: {len(job_descriptions)}")
print(f"Ejemplo de una descripción: {job_descriptions[0] if job_descriptions else 'No data'}")

# Validar que todas las entradas sean strings
if not all(isinstance(desc, str) and desc.strip() for desc in job_descriptions):
    print("Error: Hay elementos no válidos en job_descriptions.")
    exit()

# Verificar si el PDF existe
if not os.path.exists(doc_path_resume):
    print(f"Error: El archivo {doc_path_resume} no existe.")
    exit()

# Cargar el PDF del currículum
loader = UnstructuredPDFLoader(file_path=doc_path_resume)
data = loader.load()
print("done loading ...")

# Extraer el contenido de todas las páginas
if data:
    content = "\n".join([page.page_content for page in data])
else:
    print("Error: No se pudo extraer contenido del PDF.")
    exit()

# Dividir el texto en fragmentos
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
chunks = text_splitter.split_documents(data)
print("done splitting")

# Crear base de datos de vectores
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="simple-rag"
)
print("done adding to vector database ...")

# Generar embeddings para las ofertas de trabajo
job_embeddings = OllamaEmbeddings(model="nomic-embed-text").embed_documents(job_descriptions)
print("done job_embeddings adding to vector database ...")

# Generar embedding del currículum
resume_embedding = OllamaEmbeddings(model="nomic-embed-text").embed_query(content)
print("Resume embedding generated...")

# Convertir embeddings a arrays de NumPy para cálculo eficiente
job_embeddings_array = np.array(job_embeddings)

# Calcular similitud coseno entre el currículum y cada oferta de trabajo
similarities = cosine_similarity([resume_embedding], job_embeddings_array)[0]

# Obtener los índices de las 10 ofertas de trabajo más similares
top_10_indices = similarities.argsort()[-10:][::-1]
print(similarities)
# Extraer las 10 mejores ofertas de trabajo
top_10_jobs = df_jobs.iloc[top_10_indices]

# Mostrar los 10 trabajos más relevantes
print(top_10_jobs)
print(top_10_jobs.head(1))
print(top_10_jobs.columns)

# Configurar LLM y recuperación
llm = ChatOllama(model=model)

QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="You are a hiring manager and your task is to answer questions about the candidate: {question}"
)

retriever = vector_db.as_retriever()  # Empezar con recuperación simple

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

# Realizar consultas sobre el currículum
res = chain.invoke({"question": "What are the soft skills of the candidate"})
print(res)

res = chain.invoke({"question": "What are the technical skills of the candidate"})
print(res)

print(f"Total job postings: {len(df_jobs)}")

# Tiempo total de ejecución
tiempo_final = time.perf_counter() - tiempo_inicial
print("El modelo demoró:", tiempo_final, "segundos")
