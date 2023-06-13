#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test Slixmpp client connection to server"""
import asyncio

from slixmpp import ClientXMPP


def test_client_connection(run_server_fixture):
    # Create a slixmpp client
    client = ClientXMPP("test@127.0.0.1", "test")

    # Create a connection event
    client.connected_event = asyncio.Event()
    connection_callback = lambda event: client.connected_event.set()
    client.add_event_handler("connected", connection_callback)

    # Create a connection failed event
    client.connection_failed_event = asyncio.Event()
    connection_failed_callback = lambda event: (
        client.connection_failed_event.set(),
        print("Connection failed:", event),
    )
    client.add_event_handler("connection_failed", connection_failed_callback)

    # Create a disconnection event
    client.disconnected_event = asyncio.Event()
    disconnection_callback = lambda event: client.disconnected_event.set()
    client.add_event_handler("disconnected", disconnection_callback)

    # Test server connection
    client.connect()
    asyncio.get_event_loop().run_until_complete(
        asyncio.wait(
            [client.connected_event.wait(), client.connection_failed_event.wait()],
            return_when=asyncio.FIRST_COMPLETED,
        )
    )

    # Check connection
    assert client.connected_event.is_set()
    assert not client.connection_failed_event.is_set()
