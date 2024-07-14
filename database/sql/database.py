from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://root:bH01iiR12ZGtOKXbbfAPpGfi@hotaka.liara.cloud:32627/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()