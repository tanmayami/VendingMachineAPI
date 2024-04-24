# CRUD OPERATIONS FOR USERS

from fastapi import APIRouter, HTTPException
from models import User

user_router = APIRouter()
users_db = {}

#CREATE
@user_router.post("/users/")
async def create_user(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = user
    return {"message": "User {} was added successfully".format(user.username)}

#READ
@user_router.get("/users/")
async def read_users():
    return list(users_db.values())

@user_router.get("/users/{username}")
async def read_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return { "username" : username, 
             "is_seller" : users_db[username].is_seller,
             "balance_in_cents": users_db[username].balance_in_cents
    }

#UPDATE
@user_router.put("/users/{username}/seller")
async def update_seller_status(username: str, is_seller: bool):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if users_db[username].is_seller == is_seller:
        if is_seller: 
            return {"message": "User {} is already a seller".format(username)}
        else:
            return {"message": "User {} is already a not a seller".format(username)}
        
    users_db[username].is_seller = is_seller
    return { "username" : username, 
             "is_seller" : users_db[username].is_seller,
    }

#DELETE
@user_router.delete("/users/{username}")
async def delete_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[username]
    return {"message": "User {} was deleted successfully".format(username)}
