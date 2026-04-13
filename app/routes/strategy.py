from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.strategy import Strategy, StrategyStep
from ..schemas.strategy import CreateStrategySchema
from ..routes.login import _parse

strategy_bp = Blueprint("strategy", __name__, url_prefix="/strategies")


@strategy_bp.get("", strict_slashes=False)
@jwt_required()
def get_strategies():
    user_id    = int(get_jwt_identity())
    strategies = Strategy.query.filter_by(user_id=user_id).order_by(Strategy.created_at.desc()).all()
    return jsonify([s.to_dict() for s in strategies]), 200


@strategy_bp.post("", strict_slashes=False)
@jwt_required()
def create_strategy():
    user_id = int(get_jwt_identity())

    body, err = _parse(CreateStrategySchema, request.get_json(silent=True) or {})
    if err:
        return err

    strategy = Strategy(user_id=user_id, name=body.name)
    db.session.add(strategy)
    db.session.flush()  # get strategy.id before inserting steps

    for step in body.steps:
        db.session.add(StrategyStep(
            strategy_id=strategy.id,
            position=step.position,
            title=step.title,
            content=step.content,
        ))

    db.session.commit()

    return jsonify(strategy.to_dict()), 201
