from pydantic import BaseModel, conint

class User(BaseModel):
    username: str
    password: str
    is_seller: bool = False
    balance_in_cents: int = 0 

class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    seller: str

class Deposit(BaseModel):
    coins_5: conint(ge=0) = 0
    coins_10: conint(ge=0) = 0
    coins_20: conint(ge=0) = 0
    coins_50: conint(ge=0) = 0
    coins_100: conint(ge=0) = 0 