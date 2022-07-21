"""
This is the code from before that we should build off of

from fastapi import FastAPI

from routers import routes

app = FastAPI()
app.include_router(routes.router)


@app.get("/")
async def root():
    return {"message": "Default route working"}

"""

# This is the code from the DB tutorial at:
# https://fastapi.tiangolo.com/tutorial/sql-databases/

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, schemas, utils
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup/")
def create_user(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    # db_user = crud.get_user_by_email(db, email=user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_account(db=db, account=account)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: str, request: Request, db: Session = Depends(get_db)):

    # Must check authorization tokens!
    # TODO: Separate this into another function
    access_token = request.headers.get('access-token')
    utils.authenticate_token(access_token)

    print(f"In routes, account id type is: {type(account_id)}, {account_id}")
    db_user = crud.get_account(db, account_id=account_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
