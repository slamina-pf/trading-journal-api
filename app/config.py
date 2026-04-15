import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-key"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'tj_user')}"
        f":{os.getenv('DB_PASSWORD', 'tj_pass')}"
        f"@{os.getenv('DB_HOST', 'db')}"
        f":{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_NAME', 'trading_journal')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY     = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET  = os.getenv("CLOUDINARY_API_SECRET")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"
