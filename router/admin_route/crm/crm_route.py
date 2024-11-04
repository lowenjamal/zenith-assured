from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from .crm_class import CRMManagement
from schema.crm_lead import CRMUserBaseSchema
from models.crm import leads, leads_activities
from models.user.user import User
from router.user_routes.account.account import create_account
from database import engine, SessionLocal

leads.Base.metadata.create_all(bind=engine)
leads_activities.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/create-lead/")
async def create_lead(lead_data: CRMUserBaseSchema = Depends(), db: Session = Depends(get_db)):
    try:
        lead_ = CRMManagement(db).create_lead(lead_data)
        if lead_["status"] == "success":
            return lead_
    except Exception as e:
        raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})


@router.post("/bulk-upload-leads/")
async def bulk_upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        upload_file = CRMManagement(db).bulk_upload_leads(file)
        if upload_file["status"] == "success":
            return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/get-all-leads/")
async def get_all_leads(admin_id: int, db: Session = Depends(get_db)):
    try:
        leads_ = CRMManagement(db).get_all_leads(admin_id)
        if leads_:
            return {"status": "success", "message": leads_}
        else:
            return {"status": "error", "message": "no leads to fetch"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/view-lead/{lead_id:int}")
async def view_lead(admin_id: int, lead_id: int, db: Session = Depends(get_db)):
    try:
        lead_ = CRMManagement(db).view_lead(admin_id, lead_id)
        if lead_:
            return {"status": "success", "message": lead_}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.put("/edit-lead/{lead_id:int}")
async def edit_lead(admin_id: int, lead_id: int, data: CRMUserBaseSchema = Depends(), db: Session = Depends(get_db)):
    try:
        edit_lead_ = CRMManagement(db).edit_lead(admin_id, lead_id, data)
        if edit_lead_["status"] == "success":
            return {"status": "success", "message": "edited successfully"}
        else:
            return {"status": "error", "message": "unable to edit lead"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.delete("/delete_lead/{lead_id:int}")
async def delete_lead(admin_id: int, lead_id: int, db: Session = Depends(get_db)):
    try:
        delete_lead_ = CRMManagement(db).delete_lead(admin_id, lead_id)
        return delete_lead_
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)


@router.post("/activate-lead/{lead_id}")
async def activate_lead(admin_id: int, lead_id: int, db: Session = Depends(get_db)):
    try:
        activate_lead_ = CRMManagement(db).activate_lead(admin_id, lead_id)
        create_account_ = await create_account(activate_lead_.id, db)
        if create_account_["status"] == "success":
            return {"status": "success", "message": "lead activated and account activated"}
        else:
            db.rollback()
            raise HTTPException(status_code=401, detail="Unable to activate account")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/add-comment/{lead_id}")
async def add_comment(admin_id: int, lead_id: int, comment: str, db: Session = Depends(get_db)):
    try:
        comment = CRMManagement(db).add_comment(admin_id, lead_id, comment)
        return comment
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/view-comment/{lead_id}")
async def view_comments(admin_id: int, lead_id: int, db: Session = Depends(get_db)):
    try:
        comment = CRMManagement(db).view_comment(admin_id, lead_id)
        return comment
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
