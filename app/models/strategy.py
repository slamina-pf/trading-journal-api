from sqlalchemy.dialects.mysql import INTEGER, SMALLINT

from ..extensions import db


class Strategy(db.Model):
    __tablename__ = "strategies"

    id         = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name       = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    steps = db.relationship("StrategyStep", back_populates="strategy", cascade="all, delete-orphan", order_by="StrategyStep.position")
    user  = db.relationship("User", backref=db.backref("strategies", lazy="dynamic"))

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "name":       self.name,
            "steps":      [s.to_dict() for s in self.steps],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class StrategyStep(db.Model):
    __tablename__ = "strategy_steps"

    id          = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    strategy_id = db.Column(INTEGER(unsigned=True), db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    position    = db.Column(SMALLINT(unsigned=True), nullable=False)
    title       = db.Column(db.String(100), nullable=True)
    content     = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    strategy = db.relationship("Strategy", back_populates="steps")

    __table_args__ = (
        db.UniqueConstraint("strategy_id", "position", name="uq_strategy_step_position"),
    )

    def to_dict(self):
        return {
            "id":          self.id,
            "strategy_id": self.strategy_id,
            "position":    self.position,
            "title":       self.title,
            "content":     self.content,
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }
