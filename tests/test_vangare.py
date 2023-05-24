#!/usr/bin/env python

"""Tests for `vangare` package."""

import pytest
import socket

from vangare import VangareServer, GracefulExit, run_server


def raise_exit():
    raise GracefulExit()


def test_run_server():
    server = VangareServer()
    run_server(server=server, debug=True, interactive=False)


@pytest.mark.asyncio
async def test_tcp_connections():
    host = "127.0.0.1"
    server = VangareServer(host=host)
    await server.start()

    # Test client connection
    transport = socket.create_connection((host, 5222), 60)
    transport.close()

    # Test server connection
    transport = socket.create_connection((host, 5222), 60)
    transport.close()

    await server.stop()
