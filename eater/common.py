def remove_markdown_fence(json_str):
    fence_start = "```json"
    fence_end = "```"
    if json_str.startswith(fence_start):
        json_str = json_str[len(fence_start):].lstrip("\n")
        if json_str.endswith(fence_end):
            json_str = json_str[: -len(fence_end)].rstrip("\n")
    return json_str