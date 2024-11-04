from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.user.user import User
from models.crm.leads import CRMUserBase
from schema.admin import AdminCreate, AssignTaskEnum
from passlib.context import CryptContext
from datetime import datetime


class SuperAdmin:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_admins(self):
        return self.db.query(User).filter(User.user_type == "admin").order_by(desc(User.created_at)).all()

    def view_admin(self, admin_id: int):
        admin = self.db.query(User).filter(User.id == admin_id, User.user_type == "admin").first()
        user = self.db.query(User).filter(User.assigned_to == admin_id).order_by(desc(User.created_at)).all()
        return {
            "admin_profile": admin,
            "users_assigned": user
        }

    async def create_admin(self, admin_data: AdminCreate):
        hashed_password = self.pwd_context.hash(admin_data.password)
        try:
            db_admin = User(
                email=admin_data.email,
                first_name=admin_data.first_name,
                last_name=admin_data.last_name,
                password=hashed_password,
                address=admin_data.address,
                country=admin_data.country,
                phone_number=admin_data.phone_number,
                date_of_birth=admin_data.date_of_birth,
                user_type="admin",
                created_at=datetime.now()
            )
            self.db.add(db_admin)
            self.db.commit()
            self.db.refresh(db_admin)
            return {"status": "success", "message": "admin created successfully."}
        except HTTPException as e:
            raise HTTPException(status_code=403, detail="Unable to add user")

    async def delete_admin(self, admin_id: int):
        try:
            admin = self.db.query(User).filter(User.id == admin_id).first()
            if admin:
                self.db.delete(admin)
                self.db.commit()
        except HTTPException as e:
            raise HTTPException(status_code=403, detail="Unable to add user")

    async def reset_admin_password(self, admin_id: int):
        try:
            admin = self.db.query(User).filter(User.id == admin_id).first()
            if admin:
                admin.password = self.pwd_context.hash("adminpassword")
        except HTTPException as e:
            raise HTTPException(status_code=403, detail="Unable to add user")

    async def assign_task_user_to_admin(self, user_id: int, admin_id: int, assign_task: AssignTaskEnum):
        try:
            admin = self.db.query(User).filter(User.id == admin_id).first()
            user = self.db.query(User).filter(User.id == user_id).first()
            if admin and user:
                match assign_task:
                    case assign_task.assign:
                        user.assigned_to = admin.id
                    case assign_task.unassign:
                        user.assigned_to = 0
                self.db.commit()
                self.db.refresh(user)
                return {
                    "status": "success",
                    "message": f"{user.first_name} {user.last_name} is {assign_task.value}ed to {admin.first_name} {admin.last_name}"
                }
        except HTTPException as e:
            raise HTTPException(status_code=403, detail=f"Unable to assign user to admin")

    async def assign_leads_to_admin(self, lead_id: int, admin_id: int, assign_task: AssignTaskEnum):
        try:
            admin = self.db.query(User).filter(User.id == admin_id).first()
            lead = self.db.query(CRMUserBase).filter(CRMUserBase.id == lead_id).first()
            if admin and lead:
                match assign_task:
                    case assign_task.assign:
                        lead.assigned_to = admin_id
                    case assign_task.unassign:
                        lead.assigned_to = 0
                self.db.commit()
                self.db.refresh(lead)
                return {
                    "status": "success",
                    "message": f"{lead.first_name} {lead.last_name} is {assign_task.value}ed to {admin.first_name} {admin.last_name}"
                }
        except HTTPException as e:
            raise HTTPException(status_code=403, detail=f"Unable to add lead to admin, {e}")
