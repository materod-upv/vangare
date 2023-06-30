# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import asyncio

from enum import Enum
from loguru import logger
from xml import sax

from vangare.network.XMPPStreamHandler import XMPPStreamHandler

class XMLStreamProtocol(asyncio.Protocol):
    '''
    Protocol to manage the network connection between nodes in the XMPP network. Handles the transport layer.
    '''

    __slots__ = ["_state", "_transport", "_xml_parser", "_xml_writer"]

    def __init__(self):
        self._transport = None
        self._xml_parser = None
        self._xml_writer = None

    @property
    def transport(self):
        return self._transport

    def connection_made(self, transport):
        '''
        Called when a client or another server opens a TCP connection to the server
        
        :param transport: The transport object for the connection
        :type transport: asyncio.Transport
        '''
        if transport:
            self._transport = transport

            self._xml_parser = sax.make_parser()
            self._xml_parser.setFeature(sax.handler.feature_namespaces, 1)
            self._xml_parser.setContentHandler(XMPPStreamHandler(self._transport))

            logger.info(f"Connection from {self._transport.get_extra_info('peername')}")
        else:
            self._transport = None
            self._xml_parser = None
            self._xml_writer = None

            logger.error("Invalid transport")

    def connection_lost(self, exc):
        '''
        Called when a client or another server closes a TCP connection to the server

        :param exc: Exception that caused the connection to close
        :type exc: Exception
        '''
        logger.info(f"Connection lost from {self._transport.get_extra_info('peername')}: Reason {exc}")

        self._transport = None
        self._xml_parser = None
        self._xml_writer = None

    def data_received(self, data):
        '''
        Called when data is received from the client or another server

        :param data: Chunk of data received
        :type data: Byte array
        '''
        logger.debug(f"Data received: {data.decode()}")
        
        try:
            self._xml_parser.feed(data)
        except sax.SAXParseException as e:
            logger.error(f"Error parsing XML: {e}")
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")

    def eof_received(self):
        '''
        Called when the client or another server sends an EOF
        '''
        logger.debug(f"EOF received from {self._transport.get_extra_info('peername')}")

        self._transport = None
        self._xml_parser = None
        self._xml_writer = None


