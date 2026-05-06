from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models.models import User, Company, Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Your account has been deactivated. Please contact admin."}), 403

    # Check blacklisted company
    if user.role == "company" and user.company and user.company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted."}), 403

    profile = None
    if user.role == "company" and user.company:
        profile = {"approval_status": user.company.approval_status, "company_id": user.company.id, "company_name": user.company.company_name}
    elif user.role == "student" and user.student:
        profile = {"student_id": user.student.id, "name": user.student.name}

    additional_claims = {"role": user.role, "profile": profile}
    token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return jsonify({
        "access_token": token,
        "user": {**user.to_dict(), "profile": profile}
    }), 200


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json()
    required = ["email", "password", "name"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=email, role="student")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        name=data["name"],
        roll_number=data.get("roll_number"),
        branch=data.get("branch"),
        cgpa=float(data.get("cgpa", 0.0)),
        year=int(data.get("year", 1)) if data.get("year") else None,
        phone=data.get("phone"),
        skills=data.get("skills"),
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully", "user_id": user.id}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json()
    required = ["email", "password", "company_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=email, role="company")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data["company_name"],
        hr_contact=data.get("hr_contact"),
        hr_phone=data.get("hr_phone"),
        website=data.get("website"),
        description=data.get("description"),
        industry=data.get("industry"),
        approval_status="pending",
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered. Awaiting admin approval.", "user_id": user.id}), 201


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = user.to_dict()
    if user.role == "student" and user.student:
        result["profile"] = user.student.to_dict()
    elif user.role == "company" and user.company:
        result["profile"] = user.company.to_dict()

    return jsonify(result), 200
