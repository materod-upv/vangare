# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

import enum
import xml

class Namespaces(enum.Enum):
    '''
    Defines the available namespaces in the protocol.
    '''
    XMLSTREAM = "http://etherx.jabber.org/streams"
    CLIENT = "jabber:client"
    SERVER = "jabber:server"

class BaseXML(xml.etree.ElementTree.Element):
    '''
    Base class for all the xml elements. Inherits from xml.etree.ElementTree.Element.
    '''
    def __init__(self, tag, attrib={}, **extra):
        super().__init__(tag, attrib) 

    def from_string(self, xml_string):
        '''
        Parse a string to an xml element.
        '''
        element = xml.etree.ElementTree.fromstring(xml_string)
        self.tag = element.tag
        self.text = element.text
        self.tail = element.tail
        self.attrib = element.attrib   

    def to_string(self):
        '''
        Convert the xml element to a string.
        '''
        return xml.etree.ElementTree.tostring(self, encoding="utf-8", method="xml", )
    
    def open_tag(self):
        '''
        Return the open tag of the element.
        '''
        tag = '<' + self.tag + ' '
        for a in self.attrib:
            tag += a + '="' + self.attrib[a] + '" '
        tag += '>'
        return tag.encode()
    
    def close_tag(self):
        '''
        Return the close tag of the element.
        '''
        tag = '</' + self.tag + '>'
        return tag.encode()