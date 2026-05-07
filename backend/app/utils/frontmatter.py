def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata: dict[str, str] = {}
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
        if ":" in line:
            key, value = line.split(":", 1)
            clean_value = value.strip().strip('"').strip("'")
            metadata[key.strip()] = clean_value

    if end_index is None:
        return {}, text

    body = "\n".join(lines[end_index + 1 :]).strip()
    return metadata, body

