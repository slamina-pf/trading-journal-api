from sqlalchemy.dialects.mysql import INTEGER, SMALLINT

from ..extensions import db


class Strategy(db.Model):
    __tablename__ = "strategies"

    id         = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name       = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    steps = db.relationship(
        "StrategyStep",
        back_populates="strategy",
        cascade="all, delete-orphan",
        order_by="StrategyStep.position",
        primaryjoin="and_(Strategy.id == StrategyStep.strategy_id, StrategyStep.deleted_at == None)",
    )
    indicators = db.relationship(
        "StrategyIndicator",
        back_populates="strategy",
        cascade="all, delete-orphan",
        order_by="StrategyIndicator.id",
        primaryjoin="and_(Strategy.id == StrategyIndicator.strategy_id, StrategyIndicator.deleted_at == None)",
    )
    checklists = db.relationship(
        "StrategyChecklist",
        back_populates="strategy",
        cascade="all, delete-orphan",
        order_by="StrategyChecklist.id",
        primaryjoin="and_(Strategy.id == StrategyChecklist.strategy_id, StrategyChecklist.deleted_at == None)",
    )
    versions = db.relationship(
        "StrategyVersion",
        back_populates="strategy",
        order_by="StrategyVersion.version.desc()",
    )
    user = db.relationship("User", backref=db.backref("strategies", lazy="dynamic"))

    def snapshot(self):
        return {
            "name":       self.name,
            "steps":      [s.to_dict() for s in self.steps],
            "indicators": [i.to_dict() for i in self.indicators],
            "checklists": [c.to_dict() for c in self.checklists],
        }

    def to_dict(self):
        latest = self.versions[0] if self.versions else None
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "name":       self.name,
            "steps":      [s.to_dict() for s in self.steps],
            "indicators": [i.to_dict() for i in self.indicators],
            "checklists": [c.to_dict() for c in self.checklists],
            "version":    latest.version if latest else None,
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
    deleted_at  = db.Column(db.DateTime, nullable=True, default=None)

    strategy = db.relationship("Strategy", back_populates="steps", foreign_keys=[strategy_id])

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


class StrategyIndicator(db.Model):
    __tablename__ = "strategy_indicators"

    id          = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    strategy_id = db.Column(INTEGER(unsigned=True), db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at  = db.Column(db.DateTime, nullable=True, default=None)

    strategy = db.relationship("Strategy", back_populates="indicators", foreign_keys=[strategy_id])

    def to_dict(self):
        return {
            "id":          self.id,
            "strategy_id": self.strategy_id,
            "name":        self.name,
            "description": self.description,
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }


class StrategyChecklist(db.Model):
    __tablename__ = "strategy_checklists"

    id          = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    strategy_id = db.Column(INTEGER(unsigned=True), db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at  = db.Column(db.DateTime, nullable=True, default=None)

    strategy = db.relationship("Strategy", back_populates="checklists", foreign_keys=[strategy_id])

    def to_dict(self):
        return {
            "id":          self.id,
            "strategy_id": self.strategy_id,
            "name":        self.name,
            "description": self.description,
            "created_at":  self.created_at.isoformat(),
            "updated_at":  self.updated_at.isoformat(),
        }


class StrategyVersion(db.Model):
    __tablename__ = "strategy_versions"

    id          = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    strategy_id = db.Column(INTEGER(unsigned=True), db.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    version     = db.Column(SMALLINT(unsigned=True), nullable=False)
    snapshot    = db.Column(db.JSON, nullable=False)
    created_at  = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    strategy = db.relationship("Strategy", back_populates="versions")

    __table_args__ = (
        db.UniqueConstraint("strategy_id", "version", name="uq_strategy_version"),
    )

    def to_dict(self):
        return {
            "id":          self.id,
            "strategy_id": self.strategy_id,
            "version":     self.version,
            "snapshot":    self.snapshot,
            "created_at":  self.created_at.isoformat(),
        }
