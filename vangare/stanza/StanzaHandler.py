from loguru import logger
from xml import sax

class StanzaHandler(sax.ContentHandler):
    '''
    Useful class to parse a incomping stanza from the stream. Inheriting from sax.ContentHandler
    '''
    def startElementNS(self, name, qname, attrs):
        logger.debug(f"Start element NS: {qname}:{name}-> {attrs}")

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