from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from dependencies import get_token_header
from .verify_document_class import VerifyDocument
from database import SessionLocal, engine
from models.user import verification_document

verification_document.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("upload-verification-document")
async def upload_verification_document(front: UploadFile = File(...), back: UploadFile = File(None), token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    upload = VerifyDocument(db, user_id).upload_document(front, back)
    return upload
