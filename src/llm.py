from langchain.chat_models import init_chat_model

_API_KEY = "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"
_MODEL = "gpt-4o-mini"

LLM = init_chat_model(model=_MODEL, model_provider="openai", api_key=_API_KEY)