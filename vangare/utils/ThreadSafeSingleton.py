# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import threading

class ThreadSafeSingleton(type):
    """This class implements the singleton pattern in a thread-safe way."""

    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Return the singleton instance."""
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]