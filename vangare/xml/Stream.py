# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from vangare.xml import Namespaces, BaseXML

class Stream(BaseXML):
    '''
    Stream open tag to open a stream connection.
    '''
    def __init__(self, id_=None, from_=None, to=None, version=(1, 0), xml_lang="en", xmlns=Namespaces.CLIENT.value):
        super().__init__(tag="stream:stream")

        self.id = id_
        self.from_ = from_
        self.to = to
        self.version = str(version[0]) + "." + str(version[1])
        self.xml_lang = xml_lang
        self.xmlns = xmlns

        self.set("xmlns:stream", Namespaces.XMLSTREAM.value)

    @property
    def id(self):
        return self.get("id")
    
    @id.setter
    def id(self, value):
        if value:
            self.set("id", value)
        else:
            self.remove("id")

    @property
    def from_(self):
        return self.get("from")
    
    @from_.setter
    def from_(self, value):
        if value:
            self.set("from", value)
        else:
            self.remove("from")

    @property
    def to(self):
        return self.get("to")
    
    @to.setter
    def to(self, value):
        if value:
            self.set("to", value)
        else:
            self.remove("to")

    @property
    def version(self):
        return self.get("version")
    
    @version.setter
    def version(self, value):
        if value:
            self.set("version", value)
        else:
            self.remove("version")

    @property
    def xml_lang(self):
        return self.get("xml:lang")
    
    @xml_lang.setter
    def xml_lang(self, value):
        if value:
            self.set("xml:lang", value)
        else:
            self.remove("xml:lang")

    @property
    def xmlns(self):
        return self.get("xmlns")
    
    @xmlns.setter
    def xmlns(self, value):
        if value:
            self.set("xmlns", value)
        else:
            self.remove("xmlns")

    @property
    def xmlns_stream(self):
        return self.get("xmlns:stream")
    
class StreamFeatures(BaseXML):
    def __init__(self):
        super().__init__(tag="stream:features")
        