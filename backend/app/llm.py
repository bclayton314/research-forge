import os
from functools import lru_cache

from openai import OpenAI


class LLMError(Exception):
    """Raised when an LLM request cannot be completed."""


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise LLMError(
            "OPENAI_API_KEY is not configured"
        )

    return OpenAI(
        api_key=api_key,
    )


def get_model_name() -> str:
    model = os.getenv("OPENAI_MODEL")

    if not model:
        raise LLMError(
            "OPENAI_MODEL is not configured"
        )

    return model


def generate_grounded_answer(
    question: str,
    context: str,
) -> str:
    client = get_openai_client()

    try:
        response = client.responses.create(
            model=get_model_name(),
            instructions=(
                "You are ResearchForge, a research assistant. "
                "Answer only from the supplied research context. "
                "If the context does not contain enough evidence "
                "to answer the question, say that the available "
                "documents do not provide enough information. "
                "Do not invent facts or sources. "
                "When referring to evidence, preserve the supplied "
                "source labels such as [Source 1]."
            ),
            input=(
                f"Research context:\n\n{context}\n\n"
                f"Question:\n{question}"
            ),
        )

    except Exception as exc:
        raise LLMError(
            "Unable to generate an answer"
        ) from exc

    answer = response.output_text.strip()

    if not answer:
        raise LLMError(
            "The model returned an empty answer"
        )

    return answer