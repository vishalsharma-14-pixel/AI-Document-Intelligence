"""Small recursive text splitter (paragraph -> line -> sentence -> word -> char),
so we don't need to pull in LangChain just for chunking."""

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    raw_chunks = _split_recursive(text.strip(), SEPARATORS, chunk_size)
    raw_chunks = [c for c in raw_chunks if c.strip()]
    return _apply_overlap(raw_chunks, chunk_overlap)


def _split_recursive(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    sep, *rest = separators
    if sep == "":
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    parts = text.split(sep)
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current}{sep}{part}" if current else part
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(part) > chunk_size:
            chunks.extend(_split_recursive(part, rest, chunk_size))
            current = ""
        else:
            current = part
    if current:
        chunks.append(current)
    return chunks


def _apply_overlap(chunks: list[str], chunk_overlap: int) -> list[str]:
    if chunk_overlap <= 0 or len(chunks) <= 1:
        return chunks
    result = [chunks[0]]
    for chunk in chunks[1:]:
        tail = result[-1][-chunk_overlap:]
        result.append(f"{tail}{chunk}")
    return result


def chunk_units(units: list[dict], chunk_size: int, chunk_overlap: int) -> list[dict]:
    """units: [{"text", "page", "section"}] -> chunks: [{"text", "page", "section"}]"""
    chunks: list[dict] = []
    for unit in units:
        for piece in split_text(unit["text"], chunk_size, chunk_overlap):
            chunks.append({"text": piece, "page": unit.get("page"), "section": unit.get("section")})
    return chunks
