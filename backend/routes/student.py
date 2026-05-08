import os
import csv
import io
from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db, cache
from models.models import User, PlacementDrive, Application
from functools import wraps

student_bp = Blueprint("student", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def student_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "student":
            return jsonify({"error": "Student access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_student():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return user.student if user else None


# ── Profile ─────────────────────────────────────────────────────────────────────

@student_bp.route("/profile", methods=["GET"])
@student_required
def get_profile():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    return jsonify(student.to_dict()), 200


@student_bp.route("/profile", methods=["PUT"])
@student_required
def update_profile():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    data = request.get_json()
    updatable = ["name", "roll_number", "branch", "cgpa", "year", "phone", "skills"]
    for field in updatable:
        if field in data:
            if field in ("cgpa",):
                setattr(student, field, float(data[field]))
            elif field in ("year",):
                setattr(student, field, int(data[field]))
            else:
                setattr(student, field, data[field])

    db.session.commit()
    try:
        cache.delete(f"student_profile_{student.id}")
    except Exception:
        pass
    return jsonify({"message": "Profile updated", "student": student.to_dict()}), 200


@student_bp.route("/profile/resume", methods=["POST"])
@student_required
def upload_resume():
    student = get_current_student()
    if "resume" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, DOC, DOCX allowed"}), 400

    filename = f"resume_{student.id}_{secure_filename(file.filename)}"
    upload_path = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename)
    file.save(filepath)

    student.resume_path = filename
    db.session.commit()
    return jsonify({"message": "Resume uploaded", "resume_path": filename}), 200


# ── Drives ──────────────────────────────────────────────────────────────────────

@student_bp.route("/drives", methods=["GET"])
@student_required
def get_drives():
    student = get_current_student()
    search = request.args.get("q", "").strip()
    branch_filter = request.args.get("branch", "").strip()
    eligible_only = request.args.get("eligible_only", "false").lower() == "true"

    cached_key = "approved_drives"
    try:
        drives = cache.get(cached_key)
    except Exception:
        drives = None
    if not drives:
        drive_objs = PlacementDrive.query.filter_by(status="approved").order_by(PlacementDrive.created_at.desc()).all()
        drives = [d.to_dict() for d in drive_objs]
        try:
            cache.set(cached_key, drives, timeout=120)
        except Exception:
            pass

    # Apply student eligibility filter
    if eligible_only and student:
        def is_eligible(d):
            if d["eligibility_cgpa"] and student.cgpa < d["eligibility_cgpa"]:
                return False
            if d["eligibility_year"] and student.year != d["eligibility_year"]:
                return False
            branches = d["eligibility_branch"] or "All"
            if branches.lower() != "all" and student.branch:
                eligible_branches = [b.strip().lower() for b in branches.split(",")]
                if student.branch.lower() not in eligible_branches:
                    return False
            return True
        drives = [d for d in drives if is_eligible(d)]

    # Search filter
    if search:
        drives = [d for d in drives if
                  search.lower() in d.get("job_title", "").lower() or
                  search.lower() in d.get("company_name", "").lower() or
                  search.lower() in (d.get("location") or "").lower()]

    if branch_filter:
        drives = [d for d in drives if branch_filter.lower() in (d.get("eligibility_branch") or "").lower()]

    # Mark applied drives
    if student:
        applied_drive_ids = {a.drive_id for a in student.applications.all()}
        for d in drives:
            d["already_applied"] = d["id"] in applied_drive_ids

    return jsonify(drives), 200


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@student_required
def get_drive(drive_id):
    student = get_current_student()
    drive = PlacementDrive.query.filter_by(id=drive_id, status="approved").first_or_404()
    data = drive.to_dict()
    if student:
        existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
        data["already_applied"] = existing is not None
        data["application_status"] = existing.status if existing else None
    return jsonify(data), 200


# ── Applications ────────────────────────────────────────────────────────────────

@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_to_drive(drive_id):
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

    # Deadline check
    if drive.application_deadline and datetime.utcnow() > drive.application_deadline:
        return jsonify({"error": "Application deadline has passed"}), 400

    # Duplicate check
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        return jsonify({"error": "You have already applied to this drive"}), 409

    # Eligibility check: CGPA
    if drive.eligibility_cgpa and student.cgpa < drive.eligibility_cgpa:
        return jsonify({"error": f"Minimum CGPA required: {drive.eligibility_cgpa}. Your CGPA: {student.cgpa}"}), 400

    # Eligibility check: Year
    if drive.eligibility_year and student.year != drive.eligibility_year:
        return jsonify({"error": f"This drive is for year {drive.eligibility_year} students only"}), 400

    # Eligibility check: Branch
    if drive.eligibility_branch and drive.eligibility_branch.lower() != "all":
        eligible_branches = [b.strip().lower() for b in drive.eligibility_branch.split(",")]
        if student.branch and student.branch.lower() not in eligible_branches:
            return jsonify({"error": f"This drive is for {drive.eligibility_branch} students only"}), 400

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="applied",
    )
    db.session.add(application)
    db.session.commit()
    try:
        cache.delete("approved_drives")
    except Exception:
        pass
    return jsonify({"message": "Application submitted successfully", "application": application.to_dict()}), 201


@student_bp.route("/applications", methods=["GET"])
@student_required
def get_applications():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    apps = student.applications.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


# ── CSV Export (async via Celery) ──────────────────────────────────────────────

@student_bp.route("/export", methods=["POST"])
@student_required
def export_applications():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    # dispatch background task to generate CSV and email to student
    from tasks.jobs import export_applications_csv
    task = export_applications_csv.delay(student.id)
    return jsonify({
        "message": "Export started. You will receive an email once it's ready.",
        "task_id": task.id,
    }), 202


# helper kept for debugging/local download if ever needed
# (not used by default export route)
def _sync_export(student):
    apps = student.applications.order_by(Application.application_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Application ID", "Student ID", "Student Name", "Company Name", "Drive Title",
                     "Application Date", "Status", "Remarks", "Interview Date"])
    for a in apps:
        writer.writerow([
            a.id, student.id, student.name,
            a.drive.company.company_name if a.drive and a.drive.company else "",
            a.drive.job_title if a.drive else "",
            a.application_date.strftime("%Y-%m-%d") if a.application_date else "",
            a.status,
            a.remarks or "",
            a.interview_date.strftime("%Y-%m-%d") if a.interview_date else "",
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"applications_{student.id}_{date.today()}.csv"
    )
