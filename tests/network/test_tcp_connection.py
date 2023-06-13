#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test TCP connection to server."""
import socket


def test_tcp_client_connection(run_server_fixture):
    transport = socket.create_connection(("127.0.0.1", 5222), 60)
    transport.close()


def test_tcp_server_connection(run_server_fixture):
    transport = socket.create_connection(("127.0.0.1", 5269), 60)
    transport.close()
