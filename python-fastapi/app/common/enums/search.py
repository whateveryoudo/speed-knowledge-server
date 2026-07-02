from enum import Enum


class SearchContextType(str, Enum):
    KNOWLEDGE = "knowledge"
    GLOBAL = "global"

class SearchVisibilityType(str, Enum):
    PUBLIC = "public"
    RELATED = "related"
