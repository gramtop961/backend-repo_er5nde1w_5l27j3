import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Review, Proof
from backend_utils import save_upload

app = FastAPI(title="TrustHR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewOut(BaseModel):
    id: str
    company: str
    relationship: str
    rating: int
    text: str
    status: str


@app.get("/")
async def root():
    return {"message": "TrustHR backend online"}


@app.get("/test")
async def test_database():
    try:
        collections = db.list_collection_names() if db else []
        return {"backend": "ok", "db": "ok" if db else "not-configured", "collections": collections}
    except Exception as e:
        return {"backend": "ok", "db": f"error: {e}"}


@app.post("/api/proof")
async def upload_proof(file: UploadFile = File(...)):
    # Save file to local uploads folder
    content = await file.read()
    storage_path, stored_name = save_upload(
        content, file.filename, file.content_type or "application/octet-stream"
    )

    # Store metadata in DB
    proof_doc = Proof(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        storage_path=storage_path,
    )
    proof_id = create_document("proof", proof_doc.dict())
    return {"id": proof_id, "stored": stored_name}


@app.post("/api/reviews")
async def create_review(
    company: str = Form(...),
    relationship: str = Form(...),
    rating: int = Form(...),
    text: str = Form(...),
    proof_id: Optional[str] = Form(None),
):
    data = Review(
        company=company,
        relationship=relationship,
        rating=rating,
        text=text,
        proof_id=proof_id,
    )
    review_id = create_document("review", data.dict())
    return {"id": review_id, "status": "pending"}


@app.get("/api/reviews", response_model=List[ReviewOut])
async def list_reviews(company: Optional[str] = None, limit: int = 20):
    filt = {}
    if company:
        filt["company"] = company
    filt["status"] = "approved"
    docs = get_documents("review", filt, limit)
    out: List[ReviewOut] = []
    for d in docs:
        out.append(
            ReviewOut(
                id=str(d.get("_id")),
                company=d.get("company", ""),
                relationship=d.get("relationship", ""),
                rating=int(d.get("rating", 0)),
                text=d.get("text", ""),
                status=d.get("status", "pending"),
            )
        )
    return out


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
