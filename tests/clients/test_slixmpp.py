#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test Slixmpp client connection to server"""
import asyncio
import logging

from slixmpp import ClientXMPP


def test_client_connection(run_server_fixture):
    # Configure logging
    logging.basicConfig(level='DEBUG')

    # Create a slixmpp client
    client = ClientXMPP("test@127.0.0.1", "test")

    # Create a connection event callback
    client.connected_event = asyncio.Event()
    connection_callback = lambda event: client.connected_event.set()
    client.add_event_handler("connected", connection_callback)

    # Create a connection failed event callback
    client.connection_failed_event = asyncio.Event()
    connection_failed_callback = lambda event: client.connection_failed_event.set()
    client.add_event_handler("connection_failed", connection_failed_callback)

    # Create a stream negotiation event callback
    client.stream_negotiated_event = asyncio.Event()
    stream_negotiated_callback = lambda event: client.stream_negotiated_event.set()
    client.add_event_handler("negotiated", stream_negotiated_callback)

    # Create a connection failed event callback
    client.stream_negotiated_failed_event = asyncio.Event()
    stream_negotiated_failed_callback = lambda event: client.stream_negotiated_failed_event.set()
    client.add_event_handler("negotiated_failed", stream_negotiated_failed_callback)

    '''
    # Create a socket error event callback
    client.socket_error_event = asyncio.Event()
    socket_error_callback = lambda event: (
        client.socket_error_event.set(),
        print("Slixmpp socket error:", event),
    )
    client.add_event_handler("socket_error", socket_error_callback)

    # Create a disconnection event callback
    client.disconnected_event = asyncio.Event()
    disconnection_callback = lambda event: client.disconnected_event.set()
    client.add_event_handler("disconnected", disconnection_callback)

    # Create a session start event callback
    client.session_started_event = asyncio.Event()
    session_start_callback = lambda event: client.session_started_event.set()
    client.add_event_handler("session_start", session_start_callback)

    # Create a session resumption event callback
    client.session_resumed_event = asyncio.Event()
    session_resume_callback = lambda event: client.session_resumed_event.set()
    client.add_event_handler("session_resume", session_resume_callback)

    # Create a session end event callback
    client.session_ended_event = asyncio.Event()
    session_end_callback = lambda event: client.session_ended_event.set()
    client.add_event_handler("session_end", session_end_callback)

    # Create a stream error event callback
    client.stream_error_event = asyncio.Event()
    stream_error_callback = lambda event: (
        client.stream_error_event.set(),
        print("Slixmpp stream error:", event),
    )
    client.add_event_handler("stream_error", stream_error_callback)
    '''

    # Test server connection
    client.connect(use_ssl=False, force_starttls=False, disable_starttls=True)
    asyncio.get_event_loop().run_until_complete(
        asyncio.wait(
            [client.connected_event.wait(), client.connection_failed_event.wait()],
            timeout=3,
            return_when=asyncio.FIRST_COMPLETED
        )
    )

    # Check connection
    assert client.connected_event.is_set()
    assert not client.connection_failed_event.is_set()

    # Test stream negotation
    try:
        asyncio.get_event_loop().run_until_complete(
            asyncio.wait([client.stream_negotiated_event.wait()],
            timeout=3
            )
        )
    except asyncio.TimeoutError:
        assert False, "Stream negotiation timeout"

    assert client.stream_negotiated_event.is_set()
    assert not client.stream_negotiation_failed_event.is_set()
            

    # Test session start
    '''
    try:
        asyncio.get_event_loop().run_until_complete(
            asyncio.wait([client.session_started_event.wait()],
            timeout=3
            )
        )
    except asyncio.TimeoutError:
        assert False, "Session start timeout"

    assert client.session_started_event.is_set()
    '''
