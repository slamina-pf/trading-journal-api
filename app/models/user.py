from sqlalchemy.dialects.mysql import INTEGER

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    username      = db.Column(db.String(30),  nullable=False, unique=True)
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url    = db.Column(db.String(500), nullable=True,  default=None)
    bio           = db.Column(db.String(160), nullable=True,  default=None)
    is_active     = db.Column(db.Boolean,     nullable=False, default=True)
    created_at    = db.Column(db.DateTime,    nullable=False, server_default=db.func.now())
    updated_at    = db.Column(db.DateTime,    nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "avatar_url": self.avatar_url,
            "bio":        self.bio,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
