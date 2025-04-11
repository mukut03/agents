# tools/answer.py

def tool_answer(params: dict) -> str:
    """
    Return a natural language answer using LLM memory and reasoning.
    This tool is used when the LLM decides no external tool is needed.
    """
    return params.get("text") or params.get("tool_input") or str(params)


def schema_answer():
    return {
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    }
