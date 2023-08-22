import io
import pytest
import re

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

def test_bad_format(xml_parser): 
     #TODO: Test bad format message ej <message><body>test</message>

     assert True

def test_bad_namespace_prefix(xml_parser):
    