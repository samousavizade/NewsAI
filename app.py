from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import Annotated
from routes.news import router as NewsRouter
from routes.auth import router as AuthRouter
from pydantic import BaseModel
from typing import Union

from database import mongodb
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

MONGO_DETAILS = "mongodb://root:pY2hI1u1RvQrZCnb1sGdhiaP@grande-casse.liara.cloud:30435/my-app?authSource=admin&replicaSet=rs0&directConnection=true"
SQLALCHEMY_DATABASE_URL = "postgresql://root:bH01iiR12ZGtOKXbbfAPpGfi@hotaka.liara.cloud:32627/postgres"

app.include_router(NewsRouter, tags=["news"], prefix="/news")
app.include_router(AuthRouter, tags=["auth"], prefix="")

@app.on_event("startup")
async def startup():
    await mongodb.connect_to_database(MONGO_DETAILS)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the app!"}

