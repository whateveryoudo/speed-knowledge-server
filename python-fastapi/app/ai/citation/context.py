from __future__ import annotations
import contextvars
from typing import TypedDict

class CitationRef(TypedDict, total=False):
    ref: int
    single_ref: str
    document_link: str

_citations_var: contextvars.ContextVar[list[CitationRef]] = contextvars.ContextVar('citations', default=[])

def get_citations() -> list[CitationRef]:
    return list(_citations_var.get())

def append_citation(entry: CitationRef) -> None:
    _citations_var.get().append(entry)

def reset_citations() -> None:
    _citations_var.set([])

def next_ref_index() -> int:
    cur = _citations_var.get()
    if not cur:
        return 1
    return max(c["ref"] for c in cur)