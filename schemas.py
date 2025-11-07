"""
Database Schemas for TrustHR

Each Pydantic model represents a collection in your MongoDB database.
Collection name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class Review(BaseModel):
    """
    Collection: "review"
    Public, anonymized review about HR/management for a company.
    """
    company: str = Field(..., min_length=2, max_length=120, description="Company name")
    relationship: Literal["dipendente", "ex-dipendente", "candidato"] = Field(
        ..., description="Relationship to the company"
    )
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    text: str = Field(..., min_length=20, max_length=4000, description="Review body")
    status: Literal["pending", "approved", "rejected"] = Field(
        "pending", description="Moderation status"
    )
    proof_id: Optional[str] = Field(
        None, description="Reference to proof document used for verification"
    )

    @validator("company")
    def trim_company(cls, v: str) -> str:
        return v.strip()

class Proof(BaseModel):
    """
    Collection: "proof"
    Evidence of company membership uploaded privately for verification.
    Files are stored off the public feed; only metadata is stored here.
    """
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    storage_path: str = Field(..., description="Local storage path for the uploaded file")
    review_id: Optional[str] = Field(None, description="Linked review id, if any")
