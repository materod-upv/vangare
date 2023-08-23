# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import asyncio
import os
import signal
import socket
import sys

from loguru import logger

from vangare.network.XMLStreamProtocol import XMLStreamProtocol
from vangare.xml.BaseXML import Namespaces

# XMPP OFFICIAL PORTS
CLIENT_CON_PORT = 5222
SERVER_CON_PORT = 5269

async def wakeup():
    """
    This dummy task is needed to get keyboard interrupt signal on windows. Read this thread:
    https://stackoverflow.com/questions/27480967/why-does-the-asyncios-event-loop-suppress-the-keyboardinterrupt-on-windows
    """
    while True:
        await asyncio.sleep(1)

class GracefulExit(SystemExit):
    code = 1

def _raise_graceful_exit():
    raise GracefulExit()

class VangareServer:
    """Vangare server class."""

    _slots__ = [
        "_host",
        "_client_port",
        "_server_port",
        "_family",
        "_client_listener",
        "_server_listener",
        "_connection_timeout",
        "_features"
    ]

    def __init__(
        self,
        host="0.0.0.0",
        client_port=CLIENT_CON_PORT,
        server_port=SERVER_CON_PORT,
        family=socket.AF_INET,
        connection_timeout=60
    ):
        self._host = host
        self._client_port = client_port
        self._server_port = server_port
        self._family = family
        self._client_listener = None
        self._server_listener = None
        self._connection_timeout = connection_timeout
        self._features = []

    async def start(self):
        """Start the server."""

        logger.info("Starting Vangare server...")

        loop = asyncio.get_event_loop()

        # Add handlers

        self._client_listener = await loop.create_server(
            lambda: XMLStreamProtocol(
                namespace=Namespaces.CLIENT,
                connection_timeout=self._connection_timeout,
            ),
            host=self._host,
            port=self._client_port,
            family=self._family
        )

        logger.info(
            f"Server is listening clients on {self._client_listener.sockets[0].getsockname()}"
        )

        self._server_listener = await loop.create_server(
            lambda: XMLStreamProtocol(
                namespace=Namespaces.SERVER,
                connection_timeout=self._connection_timeout
            ),
            host=self._host,
            port=self._server_port,
            family=self._family
        )

        logger.info(
            f"Server is listening servers on {self._server_listener.sockets[0].getsockname()}"
        )

        logger.info("Server started...")

    async def stop(self):
        """Stop the server."""

        logger.info("Stopping Vangare server...")

        if self._client_listener and self._client_listener.is_serving():
            self._client_listener.close()
            await self._client_listener.wait_closed()

        if self._server_listener and self._server_listener.is_serving():
            self._server_listener.close()
            await self._server_listener.wait_closed()

        logger.info("Server stopped...")

    def on_command(self):
        command = sys.stdin.readline().strip()
        logger.debug(f"Received command '{command}'")

        # @TODO: Implement commands
        if command == "stop":
            _raise_graceful_exit()


def run_server(server: VangareServer, debug: bool = False, interactive: bool = False):
    loop = asyncio.new_event_loop()
    loop.set_debug(debug)

    # Add handler for graceful exit
    try:
        loop.add_signal_handler(signal.SIGINT, _raise_graceful_exit)
        loop.add_signal_handler(signal.SIGABRT, _raise_graceful_exit)
        loop.add_signal_handler(signal.SIGTERM, _raise_graceful_exit)
    except NotImplementedError:  # pragma: no cover
        # Not implemented on Windows
        pass

    # Add console command listener
    if interactive:
        loop.add_reader(sys.stdin.fileno(), server.on_command)

    try:
        # Interrupt on windows when pressing CTRL+C
        if os.name == "nt":
            loop.run_until_complete(wakeup(), name="wakeup")
        
        # Run the server
        main_task = loop.create_task(server.start(), name="main_server")
        loop.run_until_complete(main_task)
        loop.run_forever()
    except (GracefulExit, KeyboardInterrupt):  # pragma: no cover
        pass
    finally:
        # Cancel pending tasks
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

        # Close the server
        close_task = loop.create_task(server.stop(), name="close_server")
        loop.run_until_complete(close_task)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
