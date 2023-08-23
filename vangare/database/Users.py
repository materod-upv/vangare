# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import base64

from tinydb import TinyDB, Query
from scramp import ScramMechanism

from vangare.utils import ThreadSafeSingleton

# Internal password hash. Once hashed, there is no way to go back to change password storage without resetting all users' passwords.
# We cannot support other hashes without changing how passwords are saved. The difference between sha-1 and sha-1-plus is only with the channel binding, that's why we support both.
INTERNAL_HASH = "SCRAM-SHA-1"

class NonUniqueUser(Exception):
    """Exception raised when a non unique user is found on the database."""
    pass

class UserNotExists(Exception):
    """Exception raised when a user not exists in the database."""
    pass

class UsersDatabase(metaclass=ThreadSafeSingleton):
    """Singleton class for user database."""

    _slots__ = ["_db", "_users"]

    def __init__(self, db_path="db.json"):
        """Initialize the database."""
        self._db = TinyDB(db_path)

        # Create user table
        self._users = self._db.table("users")

    def add_user(self, user, password):
        """Add a new user to the database."""

        # Check username
        if self.get_user(user):
            raise NonUniqueUser("User already registered")

        m = ScramMechanism(INTERNAL_HASH)
        salt, stored_key, server_key, iteration_count = m.make_auth_info(password)

        # Add user
        self._users.insert(
            {
                "username": user,
                "salt": base64.b64encode(salt).decode(),
                "stored_key": base64.b64encode(stored_key).decode(),
                "server_key": base64.b64encode(server_key).decode(),
                "iteration_count": iteration_count,
            }
        )

    def remove_user(self, user):
        """Remove a user from the database."""
        # Check username
        if not self.get_user(user):
            raise UserNotExists("User not exists")

        User = Query()
        self._users.remove(User.username == user)

    def check_user(self, user, password):
        """Check if the user exists and the password is correct."""

        user_data = self.get_user(user)
        if not user_data:
            return False

        m = ScramMechanism(INTERNAL_HASH)
        salt, stored_key, server_key, iteration_count = m.make_auth_info(
            password, iteration_count=user_data[3], salt=user_data[0]
        )

        if stored_key == user_data[1] and server_key == user_data[2]:
            return True

        return False

    def get_user(self, user):
        """Get user data from the database."""
        
        User = Query()
        users = self._users.search(User.username == user)

        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise NonUniqueUser("Duplicated username on database")
        else:
            user_data = users[0]
            salt = base64.b64decode(user_data["salt"].encode())
            stored_key = base64.b64decode(user_data["stored_key"].encode())
            server_key = base64.b64decode(user_data["server_key"].encode())
            iteration_count = user_data["iteration_count"]

            return salt, stored_key, server_key, iteration_count