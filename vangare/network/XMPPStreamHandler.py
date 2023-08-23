# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from enum import Enum
from loguru import logger
from xml import sax
from uuid import uuid4

from vangare.xml import Namespaces, Stream, StreamFeatures

class StreamState(Enum):
    '''
    Stream connection states.
    '''
    CONNECTED = 0
    OPENED = 1

class XMPPStreamHandler(sax.ContentHandler):
    '''
    Manages the stream data an process the xml objects. Inheriting from sax.ContentHandler
    '''
    __slots__ = ["_state", "_buffer"]

    def __init__(self, buffer):
        super().__init__()
        self._state = StreamState.CONNECTED
        self._buffer = buffer

    def startDocument(self):
        pass

    def startElement(self, name, attrs):
        pass

    def startElementNS(self, name, qname, attrs):
        logger.debug(f"Start element NS: {name}:{qname}-> {attrs}")

        # Receive stream open tag
        if self._state == StreamState.CONNECTED and name[0] == Namespaces.XMLSTREAM.value and name[1] == "stream":

            # Load attributes
            attrs = dict(attrs)

            # Get attributes
            id_= str(uuid4())
            from_ = attrs.pop((None, "from"), None)
            to = attrs.pop((None, "to"), None)
            version = tuple(map(int, attrs.pop((None, "version"), "0.9").split(".")))
            lang = attrs.pop(("http://www.w3.org/XML/1998/namespace", "lang"), None)

            # Create response attributes
            stream = Stream(id_=id_, from_=to, to=from_, version=version, xml_lang=lang, xmlns=Namespaces.CLIENT)
            features = StreamFeatures()
            
            # Send response to client
            self._buffer.write(b"<?xml version='1.0'?>")
            self._buffer.write(stream.open_tag())
            self._buffer.write(features.to_string())

            # Change state
            self._state = StreamState.OPENED

            logger.info(f"Stream opened: {from_} -> {to} ({id_})")
        else:
            logger.debug(f"Unknown element: {name}:{qname}")

    def endElementNS(self, name, qname):
        logger.debug(f"End element NS: {qname}:{name}")

    def characters(self, content):
        pass

    def ignorableWhitespace(self, whitespace):
        pass

    def processingInstruction(self, target, data):
        pass

    def skippedEntity(self, name):
        pass

