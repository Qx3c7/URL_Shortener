from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/shortener")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLModel(Base):
    __tablename__ = "urls"
    short_id = Column(String, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    expires_at = Column(Float, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

