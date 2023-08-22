import asyncio
import logging

from slixmpp import ClientXMPP


class TestClientBot(ClientXMPP):
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("connection_failed", self.connection_error)
        self.add_event_handler("stream_negotiated", self.stream_negotiated)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.error = False

    async def connection_error(self, event):
        self.error = True
        self.disconnect()

    async def stream_negotiated(self, event):
        print("STREAM NEGOTIATED")

    async def start(self, event):
        print("HOLA")
        # self.send_presence()
        # print("asdasdasd")
        # await self.get_roster()
        # self.send_message(mto="test@localhost", mbody="test message", mtype="chat")
        # self.disconnect()

    async def message(self, msg):
        if msg["type"] in ("chat", "normal"):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
    xmpp = TestClientBot("test@127.0.0.1", "1234")
    xmpp.connect(use_ssl=False, force_starttls=False, disable_starttls=True)
    xmpp.process(forever=False)