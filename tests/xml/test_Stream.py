from vangare.xml import Namespaces, Stream
from xml.etree import ElementTree as ET

STREAM_TAG = b'<stream:stream id="1234567890" from="from@example.com" to="to@example.com" version="1.0" xml:lang="en" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams" />'

def test_Stream():
    stream = Stream(id_="1234567890", from_="from@example.com", to="to@example.com", version=(1, 0), xml_lang="en", xmlns=Namespaces.CLIENT.value)

    # Test properties
    assert stream.id == "1234567890"
    assert stream.from_ == "from@example.com"
    assert stream.to == "to@example.com"
    assert stream.version == "1.0"
    assert stream.xml_lang == "en"
    assert stream.xmlns == Namespaces.CLIENT.value
    assert stream.xmlns_stream == Namespaces.XMLSTREAM.value

    # Test writter
    xml_string = stream.to_string()
    assert xml_string == STREAM_TAG

