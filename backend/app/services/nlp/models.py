from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DependencyToken(BaseModel):
    token: str
    lemma: str
    dependency_label: str
    head_token: str
    part_of_speech: str

class NamedEntity(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int

class SentenceWindow(BaseModel):
    sentence: str
    previous_sentence: str
    next_sentence: str
    window_before: str
    window_after: str

class ContextMetadata(BaseModel):
    matched_text: str
    sentence: str
    previous_sentence: str
    next_sentence: str
    window_before: str
    window_after: str
    tokens: List[DependencyToken] = Field(default_factory=list)
    dependencies: List[DependencyToken] = Field(default_factory=list)
    entities: List[NamedEntity] = Field(default_factory=list)
    noun_chunks: List[str] = Field(default_factory=list)

class MatchedPhrase(BaseModel):
    matched_text: str
    label: str
    start_char: int
    end_char: int
    context: ContextMetadata
