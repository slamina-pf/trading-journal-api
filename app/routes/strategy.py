from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.strategy import Strategy, StrategyStep, StrategyIndicator, StrategyChecklist, StrategyVersion
from ..schemas.strategy import CreateStrategySchema, UpdateStrategySchema
from ..routes.login import _parse

strategy_bp = Blueprint("strategy", __name__, url_prefix="/strategies")


def _next_version(strategy_id: int) -> int:
    latest = (
        StrategyVersion.query
        .filter_by(strategy_id=strategy_id)
        .order_by(StrategyVersion.version.desc())
        .first()
    )
    return (latest.version + 1) if latest else 1


@strategy_bp.get("", strict_slashes=False)
@jwt_required()
def get_strategies():
    user_id    = int(get_jwt_identity())
    strategies = (
        Strategy.query
        .filter_by(user_id=user_id)
        .filter(Strategy.deleted_at == None)
        .order_by(Strategy.created_at.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in strategies]), 200


@strategy_bp.get("/<int:strategy_id>", strict_slashes=False)
@jwt_required()
def get_strategy(strategy_id):
    user_id  = int(get_jwt_identity())
    strategy = (
        Strategy.query
        .filter_by(id=strategy_id, user_id=user_id)
        .filter(Strategy.deleted_at == None)
        .first()
    )

    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404

    return jsonify(strategy.to_dict()), 200


@strategy_bp.post("", strict_slashes=False)
@jwt_required()
def create_strategy():
    user_id = int(get_jwt_identity())

    body, err = _parse(CreateStrategySchema, request.get_json(silent=True) or {})
    if err:
        return err

    strategy = Strategy(user_id=user_id, name=body.name)
    db.session.add(strategy)
    db.session.flush()

    for step in body.steps:
        db.session.add(StrategyStep(
            strategy_id=strategy.id,
            position=step.position,
            title=step.title,
            content=step.content,
        ))

    for indicator in body.indicators:
        db.session.add(StrategyIndicator(
            strategy_id=strategy.id,
            name=indicator.name,
            description=indicator.description,
        ))

    for checklist in body.checklists:
        db.session.add(StrategyChecklist(
            strategy_id=strategy.id,
            name=checklist.name,
            description=checklist.description,
        ))

    db.session.flush()

    db.session.add(StrategyVersion(
        strategy_id=strategy.id,
        version=1,
        snapshot=strategy.snapshot(),
    ))

    db.session.commit()

    return jsonify(strategy.to_dict()), 201


@strategy_bp.patch("/<int:strategy_id>", strict_slashes=False)
@jwt_required()
def update_strategy(strategy_id):
    user_id  = int(get_jwt_identity())
    strategy = (
        Strategy.query
        .filter_by(id=strategy_id, user_id=user_id)
        .filter(Strategy.deleted_at == None)
        .first()
    )

    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404

    body, err = _parse(UpdateStrategySchema, request.get_json(silent=True) or {})
    if err:
        return err

    if body.name is not None:
        strategy.name = body.name

    if body.indicators is not None:
        strategy.indicators.clear()
        db.session.flush()
        for indicator in body.indicators:
            strategy.indicators.append(StrategyIndicator(
                strategy_id=strategy_id,
                name=indicator.name,
                description=indicator.description,
            ))

    if body.steps is not None:
        strategy.steps.clear()
        db.session.flush()
        for step in body.steps:
            strategy.steps.append(StrategyStep(
                strategy_id=strategy_id,
                position=step.position,
                title=step.title,
                content=step.content,
            ))

    if body.checklists is not None:
        strategy.checklists.clear()
        db.session.flush()
        for checklist in body.checklists:
            strategy.checklists.append(StrategyChecklist(
                strategy_id=strategy_id,
                name=checklist.name,
                description=checklist.description,
            ))

    db.session.flush()

    db.session.add(StrategyVersion(
        strategy_id=strategy_id,
        version=_next_version(strategy_id),
        snapshot=strategy.snapshot(),
    ))

    db.session.commit()

    return jsonify(strategy.to_dict()), 200


@strategy_bp.delete("/<int:strategy_id>", strict_slashes=False)
@jwt_required()
def delete_strategy(strategy_id):
    user_id  = int(get_jwt_identity())
    strategy = (
        Strategy.query
        .filter_by(id=strategy_id, user_id=user_id)
        .filter(Strategy.deleted_at == None)
        .first()
    )

    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404

    now = datetime.now(timezone.utc)
    strategy.deleted_at = now
    for step in strategy.steps:
        step.deleted_at = now
    for indicator in strategy.indicators:
        indicator.deleted_at = now
    for checklist in strategy.checklists:
        checklist.deleted_at = now

    db.session.commit()

    return "", 204
