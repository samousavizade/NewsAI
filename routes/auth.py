from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from models.scopes import Scope

# sql db
from database import get_sqldb_session
from sqlalchemy.orm import Session
from database.sql import crud, models, schemas

import random
import jwt
from fastapi import Depends, HTTPException, Security, status, APIRouter
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ValidationError, EmailStr

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "3063b08e2160930c08b705daf897ae1b0fa12587320bfbc67af3330c4561f6d3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from database.sql import crud, models, schemas
from database import SessionMaker, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={Scope.FREE.name: Scope.FREE.value, Scope.PREMIUM.name: Scope.PREMIUM.value},
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return crud.get_user_by_username(db, username=username)
   

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_sqldb_session)]
):
    print("get_current_user Function Called...")
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        token_seed = payload.get("revoke_seed")

    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    
    user = get_user(db, username=token_username)
    if user.revoke_seed != token_seed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked! (Seed)",
            headers={"WWW-Authenticate": authenticate_value},
        )

    if user is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
        
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Security(get_current_user, scopes=[Scope.FREE.name])],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_sqldb_session)],
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # set revoke_seed
    user.revoke_seed = random.randint(1, 1e5)
    db.commit()

    access_token = create_access_token(
        # user scopes define token
        data={"sub": user.username, "revoke_seed": user.revoke_seed, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/logout")
async def logout_to_revoke_token(
    db: Annotated[Session, Depends(get_sqldb_session)],
    current_user: Annotated[schemas.User, Security(get_current_active_user, scopes=[Scope.FREE.name])],
):
    db_user = get_user(db, current_user.username)
    db_user.revoke_seed = random.randint(1, 1e5)
    db.commit()


@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/write")
async def write_a_news(
    current_user: Annotated[schemas.User, Depends(get_current_active_user,)],
):
    return 'user wrote a news.'

@router.get("/users/read")
async def read_a_news(
    current_user: Annotated[schemas.User, Security(get_current_active_user, scopes=[Scope.PREMIUM.name])],
):
    return 'user read a news.'


@router.get("/status/")
async def read_system_status(current_user: Annotated[schemas.User, Depends(get_current_active_user)]):
    return {"status": "ok"}


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_sqldb_session)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    return crud.create_user(
        db=db, 
        user=user,
        hashed_password=hashed_password,
    )

@router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_sqldb_session)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_sqldb_session)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_sqldb_session)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@router.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_sqldb_session)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
