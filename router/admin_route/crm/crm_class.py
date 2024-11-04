from fastapi import File, UploadFile
import io
from sqlalchemy.orm import Session
from sqlalchemy import desc
import csv
from passlib.context import CryptContext
from datetime import datetime
from models.crm import leads, leads_activities
from models.user.user import User
from schema.crm_lead import CRMUserBaseSchema


class CRMManagement:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_lead(self, crm_data: CRMUserBaseSchema):
        lead = leads.CRMUserBase(
            email=crm_data.email,
            first_name=crm_data.first_name,
            last_name=crm_data.last_name,
            address=crm_data.address,
            country=crm_data.country,
            phone_number=crm_data.phone_number,
            date_of_birth=crm_data.date_of_birth,
            status=crm_data.status.Not_Called,
            activated=crm_data.activated,
            created_at=datetime.now()
        )
        self.db_session.add(lead)
        self.db_session.commit()
        self.db_session.refresh(lead)
        return {"status": "success", "message": lead}

    def bulk_upload_leads(self, file: UploadFile):
        with io.TextIOWrapper(file.file, encoding='utf-8') as text_file:
            reader = csv.DictReader(text_file)
            for row in reader:
                email = row.get('email')
                first_name = row.get('first_name')
                last_name = row.get('last_name')
                address = row.get('address')
                country = row.get('country')
                phone_number = row.get('phone_number')
                date_of_birth = datetime.strptime(row.get('date_of_birth'), '%Y-%m-%d').date()
                lead = leads.CRMUserBase(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    address=address,
                    country=country,
                    phone_number=phone_number,
                    date_of_birth=date_of_birth,
                    status='Not Called',
                    activated=False,
                    created_at=datetime.now()
                )
                self.db_session.add(lead)
            self.db_session.commit()
        return {"status": "success"}

    def view_lead(self, admin_id: int, lead_id: int):
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        get_lead = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        if get_lead:
            if user_.user_type == "super_admin" or get_lead.assigned_to == admin_id:
                return get_lead

    def get_all_leads(self, admin_id: int):
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        if user_.user_type == "admin":
            return (self.db_session.query(leads.CRMUserBase).filter(
                leads.CRMUserBase.activated.is_(False), leads.CRMUserBase.assigned_to == admin_id)
                    .order_by(desc(leads.CRMUserBase.created_at)).all())
        return self.db_session.query(leads.CRMUserBase).order_by(desc(leads.CRMUserBase.created_at)).all()

    def edit_lead(self, admin_id: int, lead_id: int,  data: CRMUserBaseSchema):
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        get_lead = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        if get_lead:
            if user_.user_type == "super_admin" or get_lead.assigned_to == admin_id:
                for key, value in data:
                    setattr(get_lead, key, value)
                self.db_session.commit()
                return {"status": "success"}
            else:
                return {"status": "error"}

    def delete_lead(self, admin_id: int, lead_id: int):
        lead_ = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        if lead_:
            if user_.user_type == "super_admin":
                self.db_session.delete(lead_)
                self.db_session.commit()
                return {"status": "success"}
            else:
                return {"status": "error"}

    def activate_lead(self, admin_id: int, lead_id: int):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        lead_ = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        if user_.user_type == "super_admin" or lead_.assigned_to == admin_id:
            add_user = User(
                email=lead_.email,
                first_name=lead_.first_name,
                last_name=lead_.last_name,
                password=pwd_context.hash("default123"),
                address=lead_.address,
                country=lead_.country,
                phone_number=lead_.phone_number,
                verified=False,
                is_active=True,
                user_type="customer",
                created_at=datetime.now()
            )
            self.db_session.add(add_user)
            lead_.activated = True
            self.db_session.commit()
            self.db_session.refresh(add_user)
            return add_user

    def add_comment(self, admin_id: int, lead_id: int, comment: str):
        activities = leads_activities.CRMUserActivities(
            user_id=lead_id,
            comment=comment,
            created_at=datetime.now()
        )
        lead_ = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        if user_.user_type == "super_admin" or lead_.assigned_to == admin_id:
            if activities:
                self.db_session.add(activities)
                self.db_session.commit()
                self.db_session.refresh(activities)
                return activities

    def view_comment(self, admin_id: int, lead_id: int):
        lead_ = self.db_session.query(leads.CRMUserBase).filter(leads.CRMUserBase.id == lead_id).first()
        user_ = self.db_session.query(User).filter(User.id == admin_id).first()
        if user_.user_type == "super_admin" or lead_.assigned_to == admin_id:
            comments = self.db_session.query(leads_activities.CRMUserActivities).filter(
                leads_activities.CRMUserActivities.user_id == lead_id).order_by(
                desc(leads_activities.CRMUserActivities.created_at)).all()
            if comments:
                return comments
