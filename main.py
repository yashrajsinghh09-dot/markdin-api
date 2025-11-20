from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, get_db, Base
from models import Document
from pydantic import BaseModel
from typing import List
from datetime import datetime

# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------
app = FastAPI(
    title="Markdin API",
    description="Backend API for Markdin Platform",
    version="1.0.0"
)

# --------------------------------------------------
# CORS Middleware
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://markdin.com",
        "https://www.markdin.com",
        "https://api.markdin.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Create DB Tables
# --------------------------------------------------
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Pydantic Schemas
# --------------------------------------------------
class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --------------------------------------------------
# Root Route
# --------------------------------------------------
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Markdin API",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    UptimeRobot & Render health check.
    Checks DB connectivity too.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# --------------------------------------------------
# Ping Check (fast endpoint)
# --------------------------------------------------
@app.get("/api/ping")
def ping():
    return {"message": "pong", "status": "active"}

# --------------------------------------------------
# CRUD: Create Document
# --------------------------------------------------
@app.post("/documents/", response_model=DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    db_doc = Document(title=doc.title, content=doc.content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

# --------------------------------------------------
# CRUD: Get All Documents
# --------------------------------------------------
@app.get("/documents/", response_model=List[DocumentResponse])
def get_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Document).offset(skip).limit(limit).all()

# --------------------------------------------------
# CRUD: Get One Document
# --------------------------------------------------
@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

# --------------------------------------------------
# CRUD: Update Document
# --------------------------------------------------
@app.put("/documents/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, doc: DocumentCreate, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.title = doc.title
    document.content = doc.content
    document.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(document)
    return document

# --------------------------------------------------
# CRUD: Delete Document
# --------------------------------------------------
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully", "id": doc_id}
