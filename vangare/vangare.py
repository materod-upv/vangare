import asyncio
import signal
import socket
import sys
import typing

from loguru import logger

from network import VangareClientProtocol


class GracefulExit(SystemExit):
    code = 1


class VangareServer:
    """Vangare server class."""

    _slots__ = [
        "_host",
        "_client_port",
        "_server_port",
        "_family",
        "_client_listener",
        "_server_listener",
    ]

    def __init__(
        self,
        host="localhost",
        client_port=5222,
        server_port=5269,
        family=socket.AF_INET,
    ):
        self._host = host
        self._client_port = client_port
        self._server_port = server_port
        self._family = family
        self._client_listener = None
        self._server_listener = None

    async def start(self):
        """Start the server."""

        logger.info("Starting Vangare server...")

        loop = asyncio.get_event_loop()

        self._client_listener = await loop.create_server(
            lambda: VangareClientProtocol(),
            host=self._host,
            port=self._client_port,
            family=self._family,
        )

        logger.info(
            f"Server is listening clients on {self._client_listener.sockets[0].getsockname()}"
        )

        self._server_listener = await loop.create_server(
            lambda: VangareClientProtocol(),
            host=self._host,
            port=self._server_port,
            family=self._family,
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


def _raise_graceful_exit():
    raise GracefulExit()


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
        # Run the server
        main_task = loop.create_task(server.start(), name="main_server")
        loop.run_until_complete(main_task)
    except (GracefulExit, KeyboardInterrupt):  # pragma: no cover
        pass
    finally:
        close_task = loop.create_task(server.stop(), name="close_server")
        loop.run_until_complete(close_task)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
