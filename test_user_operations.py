import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from user_operations import create_user, read_user, read_users, update_seller_status, delete_user, get_current_user, users_db

# Dummy test users
curr_user = HTTPBasicCredentials(username="test_user", password="abc")
other_user = HTTPBasicCredentials(username="other_user", password="xyz")
update_user = HTTPBasicCredentials(username="updated_user", password="mno")

@pytest.fixture
# Clean up users_db before and after each test
def clean_users_db():
    users_db.clear()
    yield
    users_db.clear()

# Test create_user function
@pytest.mark.asyncio
async def test_create_user(clean_users_db):
    # Test valid case
    response = await create_user(username="test_user", password="abc", is_seller=True)
    assert response == {"message": "User test_user was created successfully"}
    assert len(users_db) == 1
    assert "test_user" in users_db
    assert users_db["test_user"].username == "test_user"
    assert users_db["test_user"].is_seller == True

    # Test duplicate username
    with pytest.raises(HTTPException) as exc_info:
        await create_user(username="test_user", password="abc", is_seller=False)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

# Test read_user function
@pytest.mark.asyncio
async def test_read_user(clean_users_db):
    await create_user(username="test_user", password="abc", is_seller=True)

    # Test unauthorized access
    with pytest.raises(HTTPException) as exc_info:
        await read_user(username="test_user", current_user=get_current_user(other_user))
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test valid case
    user = await read_user(username="test_user", current_user=get_current_user(curr_user))
    assert user == {"username": "test_user", "is_seller": True, "balance_in_cents": 0}

# Test read_users function
@pytest.mark.asyncio
async def test_read_users(clean_users_db):
    # Test empty users_db
    users = await read_users()
    assert len(users) == 0

    # Test non-empty users_db
    await create_user(username="user1", password="123", is_seller=True)
    await create_user(username="user2", password="456", is_seller=False)
    assert len(users_db) == 2
    assert 'user1' in users_db
    assert 'user2' in users_db

# Test update_seller_status function
@pytest.mark.asyncio
async def test_update_seller_status(clean_users_db):
    await create_user(username="test_user", password="abc", is_seller=True)
    await create_user(username="other_user", password="xyz", is_seller=False)
    await create_user(username="updated_user", password="mno", is_seller=False)

    # Test unauthorized access
    with pytest.raises(HTTPException) as exc_info:
        await update_seller_status(username="test_user", is_seller=False, current_user=get_current_user(other_user))
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test already seller status
    response = await update_seller_status(username="test_user", is_seller=True, current_user=get_current_user(curr_user))
    assert response == {"message": "User test_user is already a seller"}

    # Test already not a seller status
    response = await update_seller_status(username="other_user", is_seller=False, current_user=get_current_user(other_user))
    assert response == {"message": "User other_user is already not a seller"}

    # Test valid case
    response = await update_seller_status(username="updated_user", is_seller=True, current_user=get_current_user(update_user))
    assert response == {"username": "updated_user", "is_seller": True}

# Test delete_user function
@pytest.mark.asyncio
async def test_delete_user(clean_users_db):
    # Test unauthorized access
    await create_user(username="test_user", password="abc", is_seller=True)
    with pytest.raises(HTTPException) as exc_info:
        await delete_user(username="test_user", current_user=get_current_user(other_user))
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Test valid case
    response = await delete_user(username="test_user", current_user=get_current_user(curr_user))
    assert response == {"message": "User test_user was deleted successfully"}
    assert len(users_db) == 0
