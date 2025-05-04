def remove_markdown_fence(json_str):
    if isinstance(json_str, dict):
        return json_str
    json_str = json_str.strip()
    if json_str.startswith("```"):
        first_newline = json_str.find("\n")
        if first_newline != -1:
            json_str = json_str[first_newline:].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-3].strip()
    return json_str
