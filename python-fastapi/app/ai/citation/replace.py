from __future__ import annotations
from app.ai.citation.context import get_citations, CitationRef
import re

_REF_PATTERN = re.compile(r"【(\d+)】")


def replace_citation_brackets(text: str) -> str:
    """替换文本中的引用括号"""
    citations = get_citations()
    by_ref: dict[int, CitationRef] = {
        citation.get("ref"): citation for citation in citations
    }
    def _sub(m: re.Match[str]) -> str:
        idx = int(m.group(1))
        c = by_ref.get(idx)
        if not c:
            return m.group(0)
        return f"[此链接]({c.get('document_link')})"

    return _REF_PATTERN.sub(_sub, text)
