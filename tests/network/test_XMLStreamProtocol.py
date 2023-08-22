#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test XMLStreamProtocol class. """
import socket
import time


def test_tcp_client_connection(run_server_fixture):
    '''
    Test TCP connection to server and dead connection.
    '''
    try:
        s = socket.create_connection(("127.0.0.1", 5222), 60)
        s.close()
    except Exception as e:
        assert False, f"Connection failed: {e}"


def test_tcp_server_connection(run_server_fixture):
    '''
    Test TCP connection to server and dead connection.
    '''
    try:
        s = socket.create_connection(("127.0.0.1", 5269), 60)
        s.close()
    except Exception as e:
        assert False, f"Connection failed: {e}"

def test_tcp_broken_stream(run_server_fixture):
    '''
    Connection timeout when the client not respond to the server.
    '''
    try:
        s = socket.create_connection(("127.0.0.1", 5222), 60)
        s.sendall(b"<?xml version='1.0'?><stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' to='localhost' version='1.0'>")
        # Wait the timeout
        time.sleep(5)
        data = s.recv(1024)
        assert "connection-timeout" in data.decode()
    except Exception as e:
        assert False, f"Connection failed: {e}"

