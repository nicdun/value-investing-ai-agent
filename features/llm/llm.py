from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Callable
from features.llm.google_genai import get_google_genai_llm
from ui.cli import get_cli

cli = get_cli()


def call_llm(
    prompt: ChatPromptTemplate,
    pydantic_model: BaseModel,
) -> BaseModel:
    llm = get_google_genai_llm()

    try:
        llm = llm.with_structured_output(
            pydantic_model,
            method="json_mode",
        )
        response = llm.invoke(prompt)
        cli.display_info(f"LLM response: {response}")
        return pydantic_model.model_validate_json(response)
    except Exception as e:
        cli.display_error(f"LLM call failed: {e}")
        raise e
