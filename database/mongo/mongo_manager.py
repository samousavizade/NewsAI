from fastapi import HTTPException
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from typing import List


def id_handler(obj):
    obj['_id'] = str(obj['_id'])
    return obj

class MongoManager:
    client: AsyncIOMotorClient = None # type: ignore
    db: AsyncIOMotorDatabase = None # type: ignore

    async def connect_to_database(self, path: str):
        logging.info("Connecting to MongoDB.")
        self.client = AsyncIOMotorClient(
            path,
            maxPoolSize=10,
            minPoolSize=10
        )
        self.news_db = self.client.newsdb # specifiy the session
        logging.info("Connected to MongoDB.")

    async def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")


    async def retrieve_all_news(self, ):
        return [id_handler(news) async for news in self.news_db.news.find()]

    async def add_news(self, news_data: dict) -> dict:
        await self.news_db.news.insert_one(news_data)

    async def retrieve_news_by_id(self, id: str) -> dict:
        news = await self.news_db.news.find_one({"_id": ObjectId(id)})
        if news:
            return id_handler(news)
        
        raise HTTPException(404, detail="News with the ID not found.")


    async def update_news(self, id: str, data: dict):
        # Return false if an empty request body is sent.
        if len(data) < 1:
            return False
        news = await self.news_db.news.find_one({"_id": ObjectId(id)})
        if news:
            updated_news = await self.news_db.news.update_one(
                {"_id": ObjectId(id)}, {"$set": data}
            )
            if updated_news:
                return True
            return False


    async def delete_news(self, id: str):
        news = await self.news_db.news.find_one({"_id": ObjectId(id)})
        if news:
            await self.news_db.news.delete_one({"_id": ObjectId(id)})
            return True

