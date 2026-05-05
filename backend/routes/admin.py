from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db, cache
from models.models import User, Company, Student, PlacementDrive, Application
from functools import wraps

admin_bp = Blueprint("admin", __name__)


def safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def safe_cache_set(key, value, timeout=300):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        pass


def safe_cache_delete(key):
    try:
        cache.delete(key)
    except Exception:
        pass


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper



@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    cached = safe_cache_get("admin_dashboard")
    if cached:
        return jsonify(cached), 200

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    pending_companies = Company.query.filter_by(approval_status="pending").count()
    pending_drives = PlacementDrive.query.filter_by(status="pending").count()
    approved_drives = PlacementDrive.query.filter_by(status="approved").count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status="selected").count()

    result = {
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "pending_companies": pending_companies,
        "pending_drives": pending_drives,
        "approved_drives": approved_drives,
        "total_applications": total_applications,
        "selected_students": selected_students,
    }
    safe_cache_set("admin_dashboard", result, timeout=300)
    return jsonify(result), 200


# ── Companies ──────────────────────────────────────────────────────────────────

@admin_bp.route("/companies", methods=["GET"])
@admin_required
def get_companies():
    status = request.args.get("status")
    q = Company.query
    if status:
        q = q.filter_by(approval_status=status)
    companies = q.order_by(Company.created_at.desc()).all()
    return jsonify([c.to_dict() for c in companies]), 200


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "approved"
    company.rejection_reason = None
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    return jsonify({"message": "Company approved", "company": company.to_dict()}), 200


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json() or {}
    company.approval_status = "rejected"
    company.rejection_reason = data.get("reason", "")
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    return jsonify({"message": "Company rejected", "company": company.to_dict()}), 200


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["POST"])
@admin_required
def toggle_blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    if company.is_blacklisted:
        # Close all pending/approved drives
        for drive in company.drives.filter(PlacementDrive.status.in_(["pending", "approved"])).all():
            drive.status = "closed"
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    safe_cache_delete("approved_drives")
    action = "blacklisted" if company.is_blacklisted else "un-blacklisted"
    return jsonify({"message": f"Company {action}", "is_blacklisted": company.is_blacklisted}), 200


# ── Students ────────────────────────────────────────────────────────────────────

@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return jsonify([s.to_dict() for s in students]), 200


@admin_bp.route("/students/<int:student_id>/deactivate", methods=["POST"])
@admin_required
def toggle_deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    user.is_active = not user.is_active
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    action = "deactivated" if not user.is_active else "activated"
    return jsonify({"message": f"Student {action}", "is_active": user.is_active}), 200


# ── Drives ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/drives", methods=["GET"])
@admin_required
def get_drives():
    status = request.args.get("status")
    q = PlacementDrive.query
    if status:
        q = q.filter_by(status=status)
    drives = q.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives]), 200


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["POST"])
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "approved"
    drive.rejection_reason = None
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    safe_cache_delete("approved_drives")
    return jsonify({"message": "Drive approved", "drive": drive.to_dict()}), 200


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["POST"])
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    data = request.get_json() or {}
    drive.status = "rejected"
    drive.rejection_reason = data.get("reason", "")
    db.session.commit()
    safe_cache_delete("admin_dashboard")
    return jsonify({"message": "Drive rejected", "drive": drive.to_dict()}), 200


@admin_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@admin_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "closed"
    db.session.commit()
    safe_cache_delete("approved_drives")
    return jsonify({"message": "Drive closed"}), 200


# ── Applications ────────────────────────────────────────────────────────────────

@admin_bp.route("/applications", methods=["GET"])
@admin_required
def get_all_applications():
    apps = Application.query.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


# ── Search ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/search", methods=["GET"])
@admin_required
def search():
    query = request.args.get("q", "").strip()
    type_ = request.args.get("type", "all")  # students / companies / all

    results = {"students": [], "companies": []}

    if type_ in ("students", "all") and query:
        students = Student.query.join(User).filter(
            db.or_(
                Student.name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                Student.roll_number.ilike(f"%{query}%"),
                Student.branch.ilike(f"%{query}%"),
            )
        ).all()
        results["students"] = [s.to_dict() for s in students]

    if type_ in ("companies", "all") and query:
        companies = Company.query.join(User).filter(
            db.or_(
                Company.company_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                Company.industry.ilike(f"%{query}%"),
            )
        ).all()
        results["companies"] = [c.to_dict() for c in companies]

    return jsonify(results), 200
