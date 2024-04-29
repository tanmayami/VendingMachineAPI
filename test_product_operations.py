import pytest
from models import User
from fastapi import HTTPException, status
from product_operations import create_product, read_products, read_product, update_product, delete_product, products_db

# Create dummy users
test_user = User(username='test_user', password='abc', is_seller=True, balance=0)
unauthorized_user = User(username='unauth_user', password='123', is_seller=False, balance=10)

@pytest.fixture
# Clean up products_db before and after each test
def clean_products_db():
    products_db.clear()
    yield
    products_db.clear()

# Test create_product function
@pytest.mark.asyncio
async def test_create_product(clean_products_db):
    # Test valid case
    product = await create_product(id=1, name="Test Product", price=10.0, quantity=5, current_user=test_user)
    assert product.id == 1
    assert product.name == "Test Product"
    assert product.price == 10.0
    assert product.quantity == 5
    assert product.seller == "test_user"
    assert len(products_db) == 1  

    # Test duplicate product id
    with pytest.raises(HTTPException) as exc_info:
        await create_product(id=1, name="Duplicate Product", price=20.0, quantity=3, current_user=test_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test negative price
    with pytest.raises(HTTPException) as exc_info:
        await create_product(id=2, name="Negative Price Product", price=-5.0, quantity=3, current_user=test_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test zero quantity
    with pytest.raises(HTTPException) as exc_info:
        await create_product(id=3, name="Zero Quantity Product", price=10.0, quantity=0, current_user=test_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    # Test unauthorized user
    with pytest.raises(HTTPException) as exc_info:
        await create_product(id=4, name="Unauthorized Product", price=15.0, quantity=3, current_user=unauthorized_user)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

# Test read_products function
@pytest.mark.asyncio
async def test_read_products(clean_products_db):
    # Test empty products_db
    products = await read_products()
    assert len(products) == 0

    # Test non-empty products_db
    await create_product(id=1, name="Product 1", price=10.0, quantity=5, current_user=test_user)
    await create_product(id=2, name="Product 2", price=20.0, quantity=3, current_user=test_user)
    products = await read_products()
    assert len(products) == 2

# Test read_product function
@pytest.mark.asyncio
async def test_read_product(clean_products_db):
    # Test product not found
    with pytest.raises(HTTPException) as exc_info:
        await read_product(1)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    # Test valid case
    await create_product(id=1, name="Product 1", price=10.0, quantity=5, current_user=test_user)
    product = await read_product(1)
    assert product.id == 1
    assert product.name == "Product 1"
    assert product.price == 10.0
    assert product.quantity == 5
    assert product.seller == "test_user"

# Test update_product function
@pytest.mark.asyncio
async def test_update_product(clean_products_db):
    # Test product not found
    with pytest.raises(HTTPException) as exc_info:
        await update_product(1, name="Updated Product", price=15.0, quantity=3, current_user=test_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    # Test unauthorized user
    await create_product(id=1, name="Product 1", price=10.0, quantity=5, current_user=test_user)
    with pytest.raises(HTTPException) as exc_info:
        await update_product(1, name="Updated Product", price=15.0, quantity=3, current_user=unauthorized_user)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test valid case
    updated_product = await update_product(1, name="Updated Product", price=15.0, quantity=3, current_user=test_user)
    assert updated_product.id == 1
    assert updated_product.name == "Updated Product"
    assert updated_product.price == 15.0
    assert updated_product.quantity == 3
    assert updated_product.seller == "test_user"

# Test delete_product function
@pytest.mark.asyncio
async def test_delete_product(clean_products_db):
    # Test product not found
    await create_product(id=1, name="Product 1", price=10.0, quantity=5, current_user=test_user)
    with pytest.raises(HTTPException) as exc_info:
        await delete_product(77, current_user=test_user)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    # Test unauthorized user
    with pytest.raises(HTTPException) as exc_info:
        await delete_product(1, current_user=unauthorized_user)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test valid case
    response = await delete_product(1, current_user=test_user)
    assert response == {"message": "ProductId 1 was deleted"}
    assert len(products_db) == 0
