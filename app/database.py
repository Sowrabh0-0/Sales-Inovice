import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")

engine = create_engine(
    MYSQL_URL,
    pool_pre_ping=True,

    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 10,
        "read_timeout": 10,
        "write_timeout": 10,
        "ssl": {"ca": None},
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


