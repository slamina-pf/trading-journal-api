from flask import Blueprint, jsonify
from ..extensions import db
from sqlalchemy import text

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({"status": "ok", "db": db_status})
