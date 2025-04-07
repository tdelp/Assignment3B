from langchain_openai import OpenAIEmbeddings

_API_KEY = "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"
_MODEL = "text-embedding-3-large"

EMBEDDINGS = OpenAIEmbeddings(model=_MODEL, api_key=_API_KEY)