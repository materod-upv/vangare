# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from vangare.network import XMLStreamProtocol
from vangare.stanza import StanzaHandler
from vangare.server import GracefulExit, VangareServer, run_server

__all__ = [
    "GracefulExit",
    "VangareServer",
    "run_server",
]

__author__ = """María Ten Rodríguez"""
__email__ = "materod@upv.edu.es"
__version__ = "0.1.0"
