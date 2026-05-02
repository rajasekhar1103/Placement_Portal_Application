from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import re


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / company / student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'company', 'student')", name="check_user_role"),
        db.CheckConstraint("length(email) >= 5", name="check_email_length"),
    )

    company = db.relationship("Company", back_populates="user", uselist=False)
    student = db.relationship("Student", back_populates="user", uselist=False)

    @db.validates('email')
    def validate_email(self, key, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @db.validates('role')
    def validate_role(self, key, value):
        if value not in ['admin', 'company', 'student']:
            raise ValueError("Invalid role")
        return value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(150))
    hr_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    approval_status = db.Column(db.String(20), default="pending")  # pending/approved/rejected
    is_blacklisted = db.Column(db.Boolean, default=False)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name="check_approval_status"),
        db.CheckConstraint("length(company_name) > 0", name="check_company_name_not_empty"),
    )

    user = db.relationship("User", back_populates="company")
    drives = db.relationship("PlacementDrive", back_populates="company", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "hr_contact": self.hr_contact,
            "hr_phone": self.hr_phone,
            "website": self.website,
            "description": self.description,
            "industry": self.industry,
            "approval_status": self.approval_status,
            "is_blacklisted": self.is_blacklisted,
            "rejection_reason": self.rejection_reason,
            "email": self.user.email if self.user else None,
            "is_active": self.user.is_active if self.user else True,
            "created_at": self.created_at.isoformat(),
        }


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(50), unique=True)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float, default=0.0)
    year = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    resume_path = db.Column(db.String(300))
    skills = db.Column(db.Text)  # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.user.email if self.user else None,
            "roll_number": self.roll_number,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "year": self.year,
            "phone": self.phone,
            "resume_path": self.resume_path,
            "skills": self.skills,
            "is_active": self.user.is_active if self.user else True,
            "created_at": self.created_at.isoformat(),
        }


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text)
    eligibility_branch = db.Column(db.String(300))  # comma-separated branches or "All"
    eligibility_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.Integer)  # e.g., 4 for final year
    salary = db.Column(db.String(100))
    location = db.Column(db.String(200))
    interview_type = db.Column(db.String(50), default="In-person")  # In-person / Virtual
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")  # pending/approved/closed/rejected
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", lazy="dynamic")

    def to_dict(self, include_company=True):
        d = {
            "id": self.id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "eligibility_branch": self.eligibility_branch,
            "eligibility_cgpa": self.eligibility_cgpa,
            "eligibility_year": self.eligibility_year,
            "salary": self.salary,
            "location": self.location,
            "interview_type": self.interview_type,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "applicant_count": self.applications.count(),
            "created_at": self.created_at.isoformat(),
        }
        if include_company and self.company:
            d["company_name"] = self.company.company_name
            d["company_website"] = self.company.website
            d["company_description"] = self.company.description
        return d


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="applied")  # applied/shortlisted/selected/rejected
    remarks = db.Column(db.Text)
    interview_date = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name="unique_student_drive"),)

    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "drive_id": self.drive_id,
            "student_name": self.student.name if self.student else None,
            "student_branch": self.student.branch if self.student else None,
            "student_cgpa": self.student.cgpa if self.student else None,
            "student_roll": self.student.roll_number if self.student else None,
            "student_email": self.student.user.email if self.student and self.student.user else None,
            "company_name": self.drive.company.company_name if self.drive and self.drive.company else None,
            "job_title": self.drive.job_title if self.drive else None,
            "application_date": self.application_date.isoformat(),
            "status": self.status,
            "remarks": self.remarks,
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
