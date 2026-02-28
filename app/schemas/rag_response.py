from pydantic import BaseModel, Field
from typing import List, Optional

class RagResponse(BaseModel):
    """
    Structured response model for the RAG system.
    Ensures that the LLM output follows a strict schema for frontend consumption.
    """
    answer: str = Field(
        ..., 
        description="The direct answer to the user's question based on the context."
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="A score between 0.0 and 1.0 indicating the model's confidence in the answer."
    )
    key_terms: List[str] = Field(
        default_factory=list, 
        description="A list of key technical terms mentioned in the answer."
    )
    sources_used: bool = Field(
        ..., 
        description="True if the answer was derived from the provided context, False otherwise."
    )
    reasoning: Optional[str] = Field(
        None, 
        description="Brief explanation of how the answer was derived (chain of thought)."
    )
