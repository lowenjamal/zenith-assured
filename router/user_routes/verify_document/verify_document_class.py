from fastapi import HTTPException, UploadFile
import os
import shutil
from sqlalchemy.orm import Session
from models.user.user import User
from models.user.verification_document import DocumentVerification

UPLOAD_DIRECTORY = "verification_document/"  # relative path
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class VerifyDocument:
    def __init__(self, db: Session, user_id: int):
        self.db_session = db
        self.user_id = user_id

    def upload_document(self, front: UploadFile, back: UploadFile = None):
        try:
            user = self.db_session.query(User).filter(User.id == self.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="user account not found")
            if user.id_verified != "unverified":
                return {"status": "error", "message": "document pending verification or already verified."}
            front_filename = f"{self.user_id}_front.{front.filename.split('.')[-1]}"
            front_path = os.path.join(UPLOAD_DIRECTORY, front_filename)
            with open(front_path, "wb") as buffer:
                shutil.copyfileobj(front.file, buffer)
            back_path = None
            if back:
                back_filename = f"{self.user_id}_back.{back.filename.split('.')[-1]}"
                back_path = os.path.join(UPLOAD_DIRECTORY, back_filename)
                with open(back_path, "wb") as buffer:
                    shutil.copyfileobj(back.file, buffer)
            add_file = DocumentVerification(
                user_id=self.user_id,
                front_document_path=front_path,
                back_document_path=back_path if back_path else None
            )
            user.id_verified = 'verifying'
            self.db_session.add(add_file)
            self.db_session.commit()
            self.db_session.refresh(add_file)
            return {"status": "success",
                    "message": "Document submitted for verification. Note: Verification might take 24 - 48 hours."}
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Unable to upload documents, reason: {str(e)}")
