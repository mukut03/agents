# formatting.py

def format_behavior_spec(spec):
    """Convert AGENT_BEHAVIOR_SPEC into an LLM-readable string."""
    lines = ["\nAvailable tools:\n"]

    for tool_name, tool in spec.items():
        lines.append(f"Tool: {tool_name}")
        lines.append(f"Description: {tool.get('description', 'N/A')}")

        use_cases = tool.get("use_cases", [])
        if use_cases:
            lines.append("Use cases:")
            for case in use_cases:
                lines.append(f"- {case}")

        example = tool.get("action_example")
        if example:
            lines.append("Example action:")
            lines.append("""{\n  "tool": "%s",\n  "tool_input": %s,\n  "reasoning": "%s"\n}""" % (
                example.get("tool", ""),
                json_like(example.get("tool_input", {})),
                example.get("reasoning", "")
            ))

        if "summarize" in tool:
            lines.append("Summary format: natural language summary is returned for the tool output.")

        lines.append("\n---\n")

    return "\n".join(lines)


def json_like(obj, indent=2):
    """Nicely format Python dict as a JSON-ish string for LLM prompts."""
    import json
    return json.dumps(obj, indent=indent, ensure_ascii=False)
