from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, ARRAY
from sqlalchemy.orm import relationship

from .. import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)

    username = Column(String)

    hashed_password = Column(String)
    revoke_seed = Column(Integer)

    is_active = Column(Boolean, default=True)
    scopes = Column(ARRAY(String),)
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")