import cloudinary
from flask import Flask
from .extensions import db, migrate, jwt
from .config import Config


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
    )

    from .models import User, Strategy, StrategyStep  # noqa: F401 – needed for Alembic autogenerate

    from .routes.health import health_bp
    from .routes.login import login_bp
    from .routes.strategy import strategy_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(strategy_bp)

    return app
