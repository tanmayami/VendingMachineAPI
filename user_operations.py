# CRUD OPERATIONS FOR USERS

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, HTTPException, Depends, status
from models import User
from security import verify_password, pwd_context

security = HTTPBasic()
user_router = APIRouter()
users_db = {} #using a dictionary for this task, but for production apps would use a real DB

# Dependency to get current auth user
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = None
    if credentials.username in users_db:
        user = users_db[credentials.username]
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

#CREATE
@user_router.post("/users/")
async def create_user(username: str, password: str, is_seller: bool=False):
    if username in users_db:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    user = User(username=username,password=password,is_seller=is_seller,balance=0)
    users_db[username] = user
    hashed_password = pwd_context.hash(password)
    users_db[username].password = hashed_password
    
    return {"message": "User {} was created successfully".format(user.username)}

#READ
@user_router.get("/users/{username}")
async def read_user(username: str, current_user: User = Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Cannot access other user's details")
    if username not in users_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return { "username" : username, 
             "is_seller" : users_db[username].is_seller,
             "balance_in_cents": users_db[username].balance_in_cents
    }

@user_router.get("/users/") #used for testing/debugging purposes
async def read_users():
    return list(users_db.values())

#UPDATE
@user_router.put("/users/{username}/seller")
async def update_seller_status(username: str, is_seller: bool, current_user: User = Depends(get_current_user)):
    if username not in users_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.username != username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Cannot update other user's details")
    
    if users_db[username].is_seller == is_seller:
        if is_seller: 
            return {"message": "User {} is already a seller".format(username)}
        else:
            return {"message": "User {} is already not a seller".format(username)}
        
    users_db[username].is_seller = is_seller
    return { "username" : username, 
             "is_seller" : users_db[username].is_seller,
    }

#DELETE
@user_router.delete("/users/{username}")
async def delete_user(username: str, current_user: User = Depends(get_current_user)):
    if username not in users_db:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.username != username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Cannot delete other user")

    del users_db[username]
    return {"message": "User {} was deleted successfully".format(username)}
