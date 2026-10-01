import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./audit.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-moi-en-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))