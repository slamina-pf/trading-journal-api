from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pydantic import ValidationError

from ..extensions import db
from ..models.user import User
from ..schemas.user import RegisterSchema, LoginSchema, EditAccountSchema

login_bp = Blueprint("login", __name__, url_prefix="/auth")


def _parse(schema_cls, data: dict):
    """Validate data against a Pydantic schema.
    Returns (instance, None) on success or (None, error_response) on failure.
    """
    try:
        return schema_cls.model_validate(data), None
    except ValidationError as exc:
        errors = [{"field": e["loc"][0], "message": e["msg"]} for e in exc.errors()]
        return None, (jsonify({"errors": errors}), 422)


# ── Register ──────────────────────────────────────────────────────────────────

@login_bp.post("/register")
def register():
    body, err = _parse(RegisterSchema, request.get_json(silent=True) or {})
    if err:
        return err

    if User.query.filter_by(email=body.email).first():
        return jsonify({"error": "email already registered"}), 409

    if User.query.filter_by(username=body.username).first():
        return jsonify({"error": "username already taken"}), 409

    user = User(
        username=body.username,
        email=body.email,
        password_hash=generate_password_hash(body.password),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


# ── Login ─────────────────────────────────────────────────────────────────────

@login_bp.post("/login")
def login():
    body, err = _parse(LoginSchema, request.get_json(silent=True) or {})
    if err:
        return err

    user = User.query.filter_by(email=body.email).first()

    if not user or not check_password_hash(user.password_hash, body.password):
        return jsonify({"error": "invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "account is disabled"}), 403

    token = create_access_token(identity=str(user.id))

    return jsonify({"access_token": token, "user": user.to_dict()}), 200


# ── Edit account ──────────────────────────────────────────────────────────────

@login_bp.patch("/account")
@jwt_required()
def edit_account():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "user not found"}), 404

    body, err = _parse(EditAccountSchema, request.get_json(silent=True) or {})
    if err:
        return err

    if body.username is not None:
        existing = User.query.filter_by(username=body.username).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "username already taken"}), 409
        user.username = body.username

    if body.email is not None:
        existing = User.query.filter_by(email=body.email).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "email already registered"}), 409
        user.email = body.email

    if body.password is not None:
        user.password_hash = generate_password_hash(body.password)

    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url or None

    if body.bio is not None:
        user.bio = body.bio or None

    db.session.commit()

    return jsonify(user.to_dict()), 200
