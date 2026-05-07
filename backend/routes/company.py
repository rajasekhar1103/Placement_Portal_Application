import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db, cache
from models.models import User, Company, PlacementDrive, Application, Student
from functools import wraps
from werkzeug.utils import secure_filename

company_bp = Blueprint("company", __name__)


def company_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "company":
            return jsonify({"error": "Company access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_current_company():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return user.company if user else None


@company_bp.route("/dashboard", methods=["GET"])
@company_required
def dashboard():
    company = get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    drives = company.drives.all()
    drives_data = []
    for d in drives:
        dd = d.to_dict(include_company=False)
        dd["application_counts"] = {
            "applied": d.applications.filter_by(status="applied").count(),
            "shortlisted": d.applications.filter_by(status="shortlisted").count(),
            "selected": d.applications.filter_by(status="selected").count(),
            "rejected": d.applications.filter_by(status="rejected").count(),
        }
        drives_data.append(dd)

    return jsonify({
        "company": company.to_dict(),
        "drives": drives_data,
        "stats": {
            "total_drives": len(drives),
            "total_applicants": sum(d["applicant_count"] for d in drives_data),
        }
    }), 200


# ── Drives ──────────────────────────────────────────────────────────────────────

@company_bp.route("/drives", methods=["GET"])
@company_required
def get_drives():
    company = get_current_company()
    drives = company.drives.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict(include_company=False) for d in drives]), 200


@company_bp.route("/drives", methods=["POST"])
@company_required
def create_drive():
    company = get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    if company.approval_status != "approved":
        return jsonify({"error": "Your company must be approved by admin before creating drives"}), 403
    if company.is_blacklisted:
        return jsonify({"error": "Your company is blacklisted"}), 403

    data = request.get_json()
    required = ["job_title"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    deadline = None
    if data.get("application_deadline"):
        try:
            deadline = datetime.fromisoformat(data["application_deadline"])
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use ISO format."}), 400

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data["job_title"],
        job_description=data.get("job_description"),
        eligibility_branch=data.get("eligibility_branch", "All"),
        eligibility_cgpa=float(data.get("eligibility_cgpa", 0.0)),
        eligibility_year=int(data.get("eligibility_year", 0)) if data.get("eligibility_year") else None,
        salary=data.get("salary"),
        location=data.get("location"),
        interview_type=data.get("interview_type", "In-person"),
        application_deadline=deadline,
        status="pending",
    )
    db.session.add(drive)
    db.session.commit()
    cache.delete("admin_dashboard")
    return jsonify({"message": "Drive created. Awaiting admin approval.", "drive": drive.to_dict()}), 201


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@company_required
def get_drive(drive_id):
    company = get_current_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    return jsonify(drive.to_dict()), 200


# ── Applications ────────────────────────────────────────────────────────────────

@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_required
def get_drive_applications(drive_id):
    company = get_current_company()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    apps = drive.applications.all()
    return jsonify([a.to_dict() for a in apps]), 200


@company_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@company_required
def update_application_status(app_id):
    company = get_current_company()
    app = Application.query.get_or_404(app_id)
    drive = app.drive
    if drive.company_id != company.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    valid_statuses = ["applied", "shortlisted", "selected", "rejected", "waitlisted"]
    new_status = data.get("status")
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Choose from: {valid_statuses}"}), 400

    app.status = new_status
    app.remarks = data.get("remarks", app.remarks)
    if data.get("interview_date"):
        try:
            app.interview_date = datetime.fromisoformat(data["interview_date"])
        except ValueError:
            pass
    app.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Status updated", "application": app.to_dict()}), 200


@company_bp.route("/profile", methods=["GET"])
@company_required
def get_profile():
    company = get_current_company()
    return jsonify(company.to_dict()), 200


@company_bp.route("/profile", methods=["PUT"])
@company_required
def update_profile():
    company = get_current_company()
    data = request.get_json()
    updatable = ["hr_contact", "hr_phone", "website", "description", "industry"]
    for field in updatable:
        if field in data:
            setattr(company, field, data[field])
    db.session.commit()
    return jsonify({"message": "Profile updated", "company": company.to_dict()}), 200
