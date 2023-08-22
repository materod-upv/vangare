# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from enum import Enum
from loguru import logger
from xml import sax
from uuid import uuid4

class Namespaces(Enum):
    '''
    Defines the available namespaces in the protocol.
    '''
    XMLSTREAM = "http://etherx.jabber.org/streams"
    CLIENT = "jabber:client"

class StreamState(Enum):
    '''
    Stream connection states.
    '''
    CONNECTED = 0
    OPENED = 1

class XMLElement:
    '''
    Base class for all the xml elements.
    '''
    __slots__ = ["_tag", "_attributes"]

    def __init__(self, tag, attributes=None):
        self._tag = tag
        self._attributes = attributes

    @property
    def tag(self):
        return self._tag
    
    @property
    def attributes(self):
        return self._attributes

    def open_tag(self):
        data = '<' + self._tag
        if self._attributes:
            for (key, value) in self._attributes.items():
                data += ' ' + key + "='" + value + "'"
        data += ">"
        logger.debug(f"Open tag: {data}")

        return data.encode()

    def close_tag(self):
        data = "</" + self._tag + ">"
        logger.debug(f"Close tag: {data}")

        return data.encode()

class Stream(XMLElement):
    '''
    Stream open tag to open a stream connection.
    '''
    def __init__(self, id_=None, from_=None, to=None, version=(1, 0), xml_lang="en", xmlns=Namespaces.CLIENT, xmlns_stream=Namespaces.XMLSTREAM):
        
        attributes = {}

        if id_:
            attributes["id"] = id_
        if from_:
            attributes["from"] = from_
        if to:
            attributes["to"] = to
        if version:
            attributes["version"] = str(version[0]) + "." + str(version[1])
        if xml_lang:
            attributes["xml:lang"] = xml_lang
        if xmlns:
            attributes["xmlns"] = xmlns.value
        if xmlns_stream:
            attributes["xmlns:stream"] = xmlns_stream.value

        super().__init__("stream:stream", attributes)
    
class Features(XMLElement):
    '''
    Features tag
    '''
    def __init__(self):
        super().__init__("stream:features")

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
            open_stream = Stream(id_=id_, from_=to, to=from_, version=version, xml_lang=lang, xmlns=Namespaces.CLIENT, xmlns_stream=Namespaces.XMLSTREAM)
            features_stream = Features()
            
            # Send response to client
            self._buffer.write(b"<?xml version='1.0'?>")
            self._buffer.write(open_stream.open_tag())
            self._buffer.write(features_stream.open_tag())
            self._buffer.write(features_stream.close_tag())

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

