from fastapi import APIRouter, Body, Depends
from starlette import status
from fastapi.encoders import jsonable_encoder
from typing import Annotated, List

# mongodb 
from server.database import get_mongodb
from server.database.mongo.mongo_manager import MongoManager

from server.models.news import (
    ErrorResponseModel,
    ResponseModel,
    CreateNewsSchema,
    UpdateNewsSchema,
)

router = APIRouter()

DataBaseDependency = Annotated[MongoManager, Depends(get_mongodb)]

@router.post("/", response_description="News data added into the database", status_code=status.HTTP_201_CREATED)
async def add_news_data(db = DataBaseDependency, news: CreateNewsSchema = Body(...)):
    news = jsonable_encoder(news)
    new_news = await db.add_news(news)
    return new_news

@router.get("/", response_description="All News retrieved", status_code=status.HTTP_200_OK)
async def get_all_news(db: DataBaseDependency, ):
    news = await db.retrieve_all_news()
    return news

@router.get("/{id}", response_description="News data retrieved")
async def get_news_data(db: DataBaseDependency, id):
    news = await db.retrieve_news_by_id(id)
    if news:
        return ResponseModel(news, "News data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "News doesn't exist.")

@router.put("/{id}")
async def update_news_data(db: DataBaseDependency, id: str, req: UpdateNewsSchema = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_news = await db.update_news(id, req)
    if updated_news:
        return ResponseModel(
            "News with ID: {} name update is successful".format(id),
            "News name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the News data.",
    )

@router.delete("/{id}", response_description="News data deleted from the database")
async def delete_News_data(db: DataBaseDependency, id: str):
    deleted_news = await db.delete_news(id)
    if deleted_news:
        return ResponseModel(
            "News with ID: {} removed".format(id), "News deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "News with id {0} doesn't exist".format(id)
    )