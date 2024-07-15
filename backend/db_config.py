from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

if os.getenv("DATABASE_URL") is not None:
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = "postgresql://postgres:qwerty@localhost/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
