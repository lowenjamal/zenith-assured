from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .super_admin_class import SuperAdmin
from database import SessionLocal
from schema.admin import AdminCreate, AssignTaskEnum

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 300


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get-all-admins/")
async def get_all_admins(db: Session = Depends(get_db)):
    get_admins = SuperAdmin(db)
    return get_admins.get_admins()


@router.get("/view-admin/{admin_id}/")
async def view_admin(admin_id: int, db: Session = Depends(get_db)):
    if admin_id:
        admin = SuperAdmin(db).view_admin(admin_id)
        return admin
    else:
        return {"status": "error", "message": "admin id is important"}


@router.post("/create-admin/")
async def create_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    if admin_data:
        admin = await SuperAdmin(db).create_admin(admin_data)
        return admin
    else:
        return {"status": "error", "message": "admin id is important"}


@router.delete("/delete-admin/{admin_id}/")
async def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    if admin_id:
        admin = await SuperAdmin(db).delete_admin(admin_id)
        return admin
    else:
        return {"status": "error", "message": "admin id is important"}


@router.put("/reset-admin-password/{admin_id}/")
async def reset_admin(admin_id: int, db: Session = Depends(get_db)):
    if admin_id:
        admin = await SuperAdmin(db).reset_admin_password(admin_id)
        return admin
    else:
        return {"status": "error", "message": "admin id is important"}


@router.put("/assign-user-to-admin/")
async def assign_user_admin(user_id: int, admin_id: int, assign_task: AssignTaskEnum, db: Session = Depends(get_db)):
    if admin_id and user_id:
        admin = await SuperAdmin(db).assign_task_user_to_admin(user_id, admin_id, assign_task)
        return admin
    else:
        return {"status": "error", "message": "admin id and user id is important"}


@router.put("/assign-lead-to-admin/")
async def assign_leads_to_admin(lead_id: int, admin_id: int, assign_task: AssignTaskEnum, db: Session = Depends(get_db)):
    if admin_id and lead_id:
        admin = await SuperAdmin(db).assign_leads_to_admin(lead_id, admin_id, assign_task)
        return admin
    else:
        return {"status": "error", "message": "admin id and user id is important"}
