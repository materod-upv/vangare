""" Test XMPPStreamHandler """

import asyncio
import io
import pytest
import re
import socket

from xml import sax

from vangare.network.XMPPStreamHandler import XMPPStreamHandler

@pytest.fixture()
def buffer():
    yield io.BytesIO()

@pytest.fixture()
def xml_parser(buffer):
    # Create the parser
    xml_parser = sax.make_parser()
    xml_parser.setFeature(sax.handler.feature_namespaces, 1)
    xml_parser.setContentHandler(XMPPStreamHandler(buffer))
    xml_parser.buffer = buffer

    return xml_parser



I_STREAM_HEADER_BAD_TAG = b"""\
<?xml version='1.0' encoding='utf-16'?>\
<foobar:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='1.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_BAD_TAG  = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_bad_tag(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_BAD_TAG)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    # TODO: Error handling
    assert False


I_STREAM_HEADER_WITH_FROM = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='1.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_WITH_FROM = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_with_from(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_WITH_FROM)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert re.fullmatch(R_STREAM_HEADER_WITH_FROM, response) is not None

I_STREAM_HEADER_WITHOUT_FROM = b"""\
<?xml version='1.0'?>\
<stream:stream \
to='im.example.com' \
version='1.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_WITHOUT_FROM = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_without_from(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_WITHOUT_FROM)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert re.fullmatch(R_STREAM_HEADER_WITHOUT_FROM, response) is not None

I_STREAM_HEADER_WITHOUT_TO = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
version='1.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_WITHOUT_TO = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_without_to(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_WITHOUT_TO)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert False

I_STREAM_HEADER_IGNORE_ID = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
id='12345678-1234-1234-1234-123456789012' \
version='1.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_IGNORE_ID = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_ignore_id(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_IGNORE_ID)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    matched = re.fullmatch(R_STREAM_HEADER_IGNORE_ID, response)

    # Check the id is diferent
    assert matched is not None
    assert matched.group(1) != '12345678-1234-1234-1234-123456789012'

I_STREAM_HEADER_BAD_LANG = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='1.0' \
xml:lang='foobar' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_BAD_LANG = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_bad_lang(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_BAD_LANG)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert False

I_STREAM_HEADER_UNSUPPORTED_LANG = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='1.0' \
xml:lang='ch-CH' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_UNSUPPORTED_LANG = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_unsupported_lang(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_UNSUPPORTED_LANG)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert False

I_STREAM_HEADER_BAD_VERSION = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='foobar' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_BAD_VERSION = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_bad_version(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_BAD_VERSION)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert False

I_STREAM_HEADER_UNSUPPORTED_VERSION = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
version='11.0' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_UNSUPPORTED_VERSION = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' version='1\.0' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_unsupported_version(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_UNSUPPORTED_VERSION)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert re.fullmatch(R_STREAM_HEADER_UNSUPPORTED_VERSION, response) is not None

I_STREAM_HEADER_WITHOUT_VERSION = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_WITHOUT_VERSION = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_without_version(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_WITHOUT_VERSION)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    assert re.fullmatch(R_STREAM_HEADER_WITHOUT_VERSION, response) is not None

I_STREAM_HEADER_INVALID_NAMESPACE = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
xml:lang='en' \
xmlns='jabber:client' \
xmlns:stream='http://wrong.namespace.example.org'>"""

R_STREAM_HEADER_INVALID_NAMESPACE = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_invalid_namespace(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_INVALID_NAMESPACE)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    # @TODO: retunr <invalid-namespace/> instead of closing the stream
    assert False

I_STREAM_HEADER_INVALID_CONTENT_NS = b"""\
<?xml version='1.0'?>\
<stream:stream \
from='juliet@im.example.com' \
to='im.example.com' \
xml:lang='en' \
xmlns='jabber:foobar' \
xmlns:stream='http://etherx.jabber.org/streams'>"""

R_STREAM_HEADER_INVALID_CONTENT_NS = r"<\?xml version='1.0'\?><stream:stream from='im.example.com' to='juliet@im.example.com' id='([0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12})' xmlns='jabber:client' xmlns:stream='http://etherx\.jabber\.org/streams'>"

def test_open_stream_invalid_content_ns(xml_parser): 
    # Write the stream header
    xml_parser.feed(I_STREAM_HEADER_INVALID_CONTENT_NS)

    # Read the buffer
    response = xml_parser.buffer.getvalue().decode('utf-8')

    # Check the response
    # @TODO: retunr <invalid-namespace/> instead of closing the stream
    assert False