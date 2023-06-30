from enum import Enum
from loguru import logger
from xml import sax
from uuid import uuid4

# Define namespaces
class Namespaces(Enum):
    XMLSTREAM = "http://etherx.jabber.org/streams"
    CLIENT = "jabber:client"

class StreamState(Enum):
    CONNECTED = 0
    OPENED = 1

class XMLElement:
    __slots__ = ["_tag"]

    def __init__(self, tag):
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    def to_string(self):
        pass

class Stream(XMLElement):
    __slots__ = ["_id", "_from", "_to", "_version", "_xml_lang", "_xmlns", "_xmlns_stream"]

    def __init__(self, id_=None, from_=None, to=None, version=(1, 0), xml_lang="en", xmlns=Namespaces.CLIENT, xmlns_stream=Namespaces.XMLSTREAM):
        super().__init__("stream:stream")

        self._tag = "stream:stream"
        self._id = id_
        self._from = from_
        self._to = to
        self._version = version
        self._xml_lang= xml_lang
        self._xmlns = xmlns
        self._xmlns_stream = xmlns_stream

    @property
    def id_(self):
        return self._id

    @property
    def from_(self):
        return self._from

    @property
    def to(self):
        return self._to

    @property
    def version(self):
        return self._version
    
    @property
    def xml_lang(self):
        return self._xml_lang
    
    @property
    def xmlns(self):
        return self._xmlns
    
    @property
    def xmlns_stream(self):
        return self._xmlns_stream

    def from_xml(self, name, qname, attrs):
        pass

    def to_string(self):
        data = b"<stream:stream "
        if self._from:
            data += b"from='" + self._from.encode() + b"' "
        if self._to:
            data += b"to='" + self._to.encode() + b"' "
        if self._id:
            data += b"id='" + self._id.encode() + b"' "
        if self._version:
            data += b"version='" + str(self._version[0]).encode() + b"." + str(self._version[1]).encode() + b"' "
        if self._xml_lang:
            data += b"xml:lang='" + self._xml_lang.encode() + b"' "
        if self._xmlns:
            data += b"xmlns='" + self._xmlns.value.encode() + b"' "
        if self._xmlns_stream:
            data += b"xmlns:stream='" + self._xmlns_stream.value.encode() + b"' "
        data += b">"

        return data

class XMPPStreamHandler(sax.ContentHandler):
    '''
    Manages the stream data an process the xml objects. Inheriting from sax.ContentHandler
    '''
    __slots__ = ["_state", "_buffer"]

    def __init__(self, buffer):
        super().__init__()

        self._state = StreamState.CONNECTED

        self._buffer = buffer

    def startElementNS(self, name, qname, attrs):
        logger.debug(f"Start element NS: {name}:{qname}-> {attrs}")

        # Receive stream open tag
        if self._state == StreamState.CONNECTED and name[0] == Namespaces.XMLSTREAM.value and name[1] == "stream":

            # Load attributes
            attrs = dict(attrs)

            from_ = attrs.pop((None, "from"), None)
            to = attrs.pop((None, "to"), None)
            version = tuple(map(int, attrs.pop((None, "version"), "0.9").split(".")))
            lang = attrs.pop(("xml", "lang"), None)

            # Create response attributes
            response_stream = Stream(id_=str(uuid4()), from_=to, to=from_, version=version, xml_lang=lang, xmlns=Namespaces.CLIENT, xmlns_stream=Namespaces.XMLSTREAM)
            
            # Send response to client
            self._buffer.write(b"<?xml version='1.0'?>")
            self._buffer.write(response_stream.to_string())

    def endElementNS(self, name, qname):
        logger.debug(f"End element NS: {qname}:{name}")

    def characters(self, content):
        logger.debug(f"Characters: {content}")

    def ignorableWhitespace(self, whitespace):
        logger.debug(f"Ignorable whitespace: {whitespace}")

    def processingInstruction(self, target, data):
        logger.debug(f"Processing instruction: {target} -> {data}")

    def skippedEntity(self, name):
        logger.debug(f"Skipped entity: {name}")

