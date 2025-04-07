# src/vectorstore.py

from embeddings import EMBEDDINGS
from langchain_milvus import Milvus
from pymilvus import connections, utility

MILVUS_URI = "http://localhost:19530"
DATABASE_NAME = "assignment_rag"
COLLECTION_NAME = "rag_collection"

# 1. Connect to Milvus
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

# 2. Drop collection if needed
def drop_collection():
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)

# 3. LangChain-compatible VECTOR_STORE (creates collection on demand)
VECTOR_STORE = Milvus(
    embedding_function=EMBEDDINGS,
    connection_args={
        "uri": MILVUS_URI,
        "db_name": DATABASE_NAME
    },
    collection_name=COLLECTION_NAME,
    index_params={"index_type": "FLAT", "metric_type": "COSINE"},
    auto_id=True,
)
