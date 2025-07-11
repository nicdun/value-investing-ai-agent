from langchain.chat_models import init_chat_model

_google_genai_llm = init_chat_model("google_genai:gemini-2.5-flash")


def get_google_genai_llm():
    return _google_genai_llm
