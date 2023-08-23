# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import asyncio

from loguru import logger
from xml import sax

from vangare.network.StreamAlivenessMonitor import StreamAlivenessMonitor
from vangare.network.XMPPStreamHandler import XMPPStreamHandler
from vangare.xml import Namespaces


class XMLStreamProtocol(asyncio.Protocol):
    '''
    Protocol to manage the network connection between nodes in the XMPP network. Handles the transport layer.
    '''

    __slots__ = ["_transport", "_xmlns", "_xml_parser", "_connection_timeout", "_timeout_monitor"]

    def __init__(self, namespace=Namespaces.CLIENT, connection_timeout=None):
        self._xmlns = namespace
        self._transport = None
        self._xml_parser = None
        self._timeout_monitor = None
        self._connection_timeout = connection_timeout

    def connection_made(self, transport):
        '''
        Called when a client or another server opens a TCP connection to the server
        
        :param transport: The transport object for the connection
        :type transport: asyncio.Transport
        '''
        if transport:
            self._transport = transport

            self._xml_parser = sax.make_parser()
            self._xml_parser.setFeature(sax.handler.feature_namespaces, True)
            self._xml_parser.setFeature(sax.handler.feature_external_ges, False)
            self._xml_parser.setContentHandler(XMPPStreamHandler(self._transport))

            if self._connection_timeout:
                self._timeout_monitor = StreamAlivenessMonitor(timeout=self._connection_timeout, callback=self.connection_timeout)

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

        self._timeout_monitor.reset()
        
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

    def connection_timeout(self):
        '''
        Called when the stream is not responding for a long tikem
        '''
        logger.debug(f"Connection timeout from {self._transport.get_extra_info('peername')}")

        self._transport.write(b"<connection-timeout/>")
        self._transport.close()

        self._transport = None
        self._xml_parser = None
        self._xml_writer = None


