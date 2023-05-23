import asyncio


class VangareClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        print("Connection from {}".format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print("Data received: {!r}".format(message))

        print("Send: {!r}".format(message))
        self.transport.write(data)

        print("Close the client socket")
        self.transport.close()
