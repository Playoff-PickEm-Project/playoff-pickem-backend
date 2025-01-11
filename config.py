import os

class Config:
    # Using the internal PostgreSQL database URL
    SQLALCHEMY_DATABASE_URI = "postgresql://akhil:25JdKdhLwEwqxRpal6ldJSxWOQRDL1X8@dpg-cu129kdsvqrc73em1620-a/playoff_pickem"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional but recommended for performance
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")  # Optional: Secret key for session management
