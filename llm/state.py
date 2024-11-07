from typing import Optional, TypedDict


class GraphState(TypedDict):
    question: Optional[str]
    classification: Optional[str]
    response: Optional[str]
