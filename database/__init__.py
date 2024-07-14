from server.database.mongo.mongo_manager import MongoManager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

mongodb = MongoManager()

async def get_mongodb() -> MongoManager:
    return mongodb

SQLALCHEMY_DATABASE_URL = "postgresql://root:bH01iiR12ZGtOKXbbfAPpGfi@hotaka.liara.cloud:32627/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_sqldb_session():
    session = SessionMaker()
    try:
        yield session
    finally:
        session.close()
