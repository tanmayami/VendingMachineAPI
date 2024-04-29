import pytest
from fastapi import HTTPException, status
from vending_operations import deposit_coins, buy_products, reset_deposit, compute_change
from models import User, Deposit
from user_operations import users_db, create_user
from product_operations import products_db, create_product

# Dummy test users
zero_balance_user = User(username="test_user", password="abc", is_seller=True, balance_in_cents=0)
buyer = User(username="buyer", password="xyz", is_seller=False, balance_in_cents=500)
reset_user = User(username="reset_user", password="mno", is_seller=False, balance_in_cents=100)

@pytest.fixture
# Clean up users_db and products_db before and after each test
def clean_users_and_products_db():
    users_db.clear()
    products_db.clear()
    yield
    users_db.clear()
    products_db.clear()

# Test deposit_coins function
@pytest.mark.asyncio
async def test_deposit_coins(clean_users_and_products_db):
    await create_user(username="test_user", password="abc", is_seller=True)

    # Test deposit with valid input
    await deposit_coins(Deposit(coins_5=2, coins_10=3, coins_20=1, coins_50=0, coins_100=0), current_user=zero_balance_user)
    assert users_db["test_user"].balance_in_cents == 60

    await deposit_coins(Deposit(coins_5=0, coins_10=0, coins_20=0, coins_50=1, coins_100=1), current_user=zero_balance_user)
    assert users_db["test_user"].balance_in_cents == 210

# Test compute_change function
def test_compute_change():
    change = compute_change(123)
    assert change == {"change_given": {"100": 1, "50": 0, "20": 1, "10": 0, "5": 0}, "unpaid_cents": 3}

    change = compute_change(55)
    assert change == {"change_given": {"100": 0, "50": 1, "20": 0, "10": 0, "5": 1}, "unpaid_cents": 0}

    change = compute_change(0)
    assert change == {"change_given": {"100": 0, "50": 0, "20": 0, "10": 0, "5": 0}, "unpaid_cents": 0}

# Test buy_products function
@pytest.mark.asyncio
async def test_buy_products(clean_users_and_products_db):
    # Prepare data
    await create_product(id=1, name="Soda", price=1.50, quantity=10, current_user=zero_balance_user)
    users_db["buyer"] = buyer

    # Test buying with valid input
    response = await buy_products(product_id=1, quantity=2, current_user=buyer)
    assert response == {
        "message": "ProductId 1 purchased successfully",
        "quanity_purchased": 2,
        "total_cost": 300,
        "change": {"change_given": {"100": 2, "50": 0, "20": 0, "10": 0, "5": 0}, "unpaid_cents": 0}
    }
    assert users_db["buyer"].balance_in_cents == 200
    assert products_db[1].quantity == 8

    # Test buying with insufficient balance
    with pytest.raises(HTTPException) as exc_info:
        await buy_products(product_id=1, quantity=5, current_user=buyer)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test buying with invalid product_id
    with pytest.raises(HTTPException) as exc_info:
        await buy_products(product_id=99, quantity=1, current_user=buyer)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    # Test buying with insufficient quantity
    with pytest.raises(HTTPException) as exc_info:
        await buy_products(product_id=1, quantity=15, current_user=buyer)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test buying seller's own product
    with pytest.raises(HTTPException) as exc_info:
        await buy_products(product_id=1, quantity=1, current_user=zero_balance_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

# Test reset_deposit function
@pytest.mark.asyncio
async def test_reset_deposit(clean_users_and_products_db):
    users_db["reset_user"] = reset_user

    # Test reset deposit with valid input
    response = await reset_deposit(username="reset_user")
    assert response == {"message": "Deposit reset successful"}
    assert users_db["reset_user"].balance_in_cents == 0

    # Test reset deposit with invalid user
    with pytest.raises(HTTPException) as exc_info:
        await reset_deposit(username="non_existent_user")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
