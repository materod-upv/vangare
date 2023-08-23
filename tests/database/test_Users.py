# Tests for the Users class

import os
import pytest

from vangare.database.Users import UsersDatabase, NonUniqueUser, UserNotExists

@pytest.fixture
def db():
    db = UsersDatabase(db_path="testdb.json")
    yield db
    del db
    os.remove("testdb.json")

def test_UsersDatabase(db):
    # Register a new user
    db.add_user("user", "password")

    # Check if the user exists
    assert db.check_user("user", "password")

    # Duplicate user
    with pytest.raises(NonUniqueUser):
        db.add_user("user", "password2")

    # Check if the user doesn't exist
    assert not db.check_user("wrong_user", "password")
    assert not db.check_user("user", "wrong_password")

    # Delete user
    db.remove_user("user")
    assert not db.check_user("user", "password")

    # Remove invalid user
    with pytest.raises(UserNotExists):
        db.remove_user("wrong_user")
