""" Test XMPPStreamHandler """

import asyncio

@pytest.fixture()
async def server(pair_sockets):
    loop = asyncio.get_running_loop()
    tc, server = await loop.create_connection(
        lambda: XMLStreamProtocol("jabber:client", hosts=["localhost"]),
        sock=pair_sockets[0],
    )
    yield server
    del server

async def test_stream_closed(self, server):
    print(server._status)