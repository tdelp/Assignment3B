import glob
import chainlit as cl
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from vectorstore import VECTOR_STORE, drop_collection
from llm import LLM
from util import debugprint, pad_fields, rename_fields

# ----------------------------
# 1. Load and preprocess documents
# ----------------------------
PDF_GLOB = "src/data/*.pdf"
pdf_files = glob.glob(PDF_GLOB)
pdf_docs = []
for file in pdf_files:
    try:
        loaded = PyPDFLoader(file).load()
        pdf_docs.extend(loaded)
    except Exception as e:
        debugprint(f"Error loading {file}: {e}")

print(f"Loaded {len(pdf_docs)} PDF documents")

URL_FILE = "src/data/web_urls.txt"
web_docs = []
try:
    with open(URL_FILE) as f:
        web_urls = [url.strip() for url in f.readlines() if url.strip()]
    web_loader = WebBaseLoader(web_urls)
    web_docs = web_loader.load()
except Exception as e:
    debugprint(f"Error loading URLs: {e}")

print(f"Loaded {len(web_docs)} web documents")


all_docs = pdf_docs + web_docs
print(f"Total loaded: {len(all_docs)} documents")

pad_fields(all_docs)
rename_fields(all_docs)

# ----------------------------
# 2. Chunk and store in vector DB
# ----------------------------
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(all_docs)
print(f"Split into {len(chunks)} text chunks")

drop_collection()
VECTOR_STORE.add_documents(chunks)
print(f"Indexed {len(chunks)} chunks into Milvus")

# ----------------------------
# 3. Tool: Retrieve from vector DB
# ----------------------------
@tool
def retrieve(query: str) -> str:
    """Retrieve relevant documents from the vector store given a user query."""
    retrieved_docs = VECTOR_STORE.similarity_search(query, k=5)
    
    if not retrieved_docs:
        return "No relevant documents found for your question."

    doc_strings = [
        f"## Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in retrieved_docs
    ]
    return "\n\n".join(doc_strings)

# ----------------------------
# 4. Set up Agent using LLM and system message
# ----------------------------
system_prompt = "You are a helpful assistant that answers questions using research papers and trusted sources."
LLM_WITH_PROMPT = LLM.bind(system_prompt=system_prompt)

AGENT = create_react_agent(
    LLM_WITH_PROMPT,
    [retrieve],
)

# ----------------------------
# 5. Chainlit UI Handler
# ----------------------------
@cl.on_message
async def on_message(message: cl.Message):
    if not message.content.strip():
        await cl.Message(content="Please enter a question.").send()
        return

    config = {"configurable": {"thread_id": cl.context.session.id}}

    try:
        result = AGENT.invoke(
            {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message.content}
                ]
            },
            config=config
        )

        #print("Agent result:", result)

        # Extract final assistant response from message list
        if isinstance(result, dict) and "messages" in result:
            for msg in reversed(result["messages"]):
                if hasattr(msg, "content") and msg.content.strip():
                    await cl.Message(content=msg.content.strip()).send()
                    return

        await cl.Message(content="No response generated.").send()
    except Exception as e:
        print("Error during agent execution:", e)
        await cl.Message(content="Something went wrong while generating a response.").send()
