from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    query: str

class SearchResponse(BaseModel):
    question: str
    answer: str
    title: str
    source_url: str
    confidence: float
    alternative_results: List[dict]