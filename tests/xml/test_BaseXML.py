from vangare.xml import BaseXML

def test_BaseXML():
    node = BaseXML("test", attrib={"a": "b"})

    assert node.tag == "test"
    assert node.attrib.get("a") == "b"

def test_BaseXML_from_string():
    xml = '<test a="b" />'

    node = BaseXML("dummy")
    node.from_string(xml)

    assert node.tag == "test"
    assert node.attrib.get("a") == "b"

def test_BaseXML_to_string():
    xml = b'<test a="b" />'

    node = BaseXML("test", attrib={"a": "b"})

    assert node.to_string() == xml

def test_BaseXML_open_tag():
    xml = b'<test a="b" >'

    node = BaseXML("test", attrib={"a": "b"})

    assert node.open_tag() == xml

def test_BaseXML_close_tag():
    xml = b'</test>'

    node = BaseXML("test", attrib={"a": "b"})

    assert node.close_tag() == xml
    