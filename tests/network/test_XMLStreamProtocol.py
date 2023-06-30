import asyncio
import pytest
import pytest_asyncio
import socket

from vangare.network import XMLStreamProtocol
from datetime import timedelta


STREAM_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

WRONG_NAMESPACE_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://wrong.namespace.example.org" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

MISSING_TO_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
xml:lang='en' \
version="1.0">"""

UNKNOWN_TO_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="unknown" \
xml:lang='en' \
version="1.0">"""

BAD_FORMAT_MSG = b"""\
<message>\
<body>No closing tag!\
</message>"""

BAD_NAMESPACE_HEADER = b"""\
<?xml version="1.0"?>\
<foobar:stream xmlns="jabber:client" \
xmlns:foobar="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

HOST_UNKNOWN_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="unknown.es" \
xml:lang='en' \
version="1.0">"""

BAD_VERSION_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="foobar">"""

INVALID_NAMESPACE_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://wrong.namespace.example.org" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

INVALID_DEFAULT_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:wrong" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

UNSUPPORTED_ENCODING_HEADER = b"""\
<?xml version="1.0" encoding="utf-16"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="1.0">"""

UNSUPPORTED_VERSION_HEADER = b"""\
<?xml version="1.0"?>\
<stream:stream xmlns="jabber:client" \
xmlns:stream="http://etherx.jabber.org/streams" \
to="localhost" \
xml:lang='en' \
version="11.0">"""

STREAM_FOOTER = b"""\
</stream:stream>"""


class DummyClientProtocol(asyncio.Protocol):
    """
    Useful class for testing as a client
    """

    @property
    def get_data(self):
        return self._data

    def __init__(self):
        self._transport = None
        self.on_connection = asyncio.Event()
        self.on_response = asyncio.Event()
        self.on_close = asyncio.Event()
        self._data = None

    def connection_made(self, transport):
        self._transport = transport
        self.on_connection.set()

    def data_received(self, data):
        print(f"DATA: {data}")
        self._data = data
        self.on_response.set()

    def eof_received(self):
        pass

    def connection_lost(self, exc):
        self.on_close.set()

    def send_data(self, data):
        self._transport.write(data)

    def close(self):
        self._transport.close()


@pytest.fixture()
def pair_sockets():
    sockets = socket.socketpair()
    return sockets


@pytest_asyncio.fixture
async def client(pair_sockets):
    loop = asyncio.get_running_loop()
    tc, client = await loop.create_connection(
        protocol_factory=lambda: DummyClientProtocol(), sock=pair_sockets[1]
    )
    yield client
    del client

@pytest_asyncio.fixture
async def server(pair_sockets):
    loop = asyncio.get_running_loop()
    tc, server = await loop.create_connection(
        lambda: XMLStreamProtocol(),
        sock=pair_sockets[0],
    )
    yield server
    del server


class TestXMLStreamProtocol:
    @pytest.mark.asyncio
    async def test_stream_closed(self, client, server):
        client.send_data(STREAM_HEADER)
        await client.on_response.wait()

        print(client.get_data())
    """
        
        await client.on_response

        client.send_data(STREAM_FOOTER)
        await client.on_response

        client.close()
        await client.on_close
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_stream_error_during_setup(self, client, server):
        client.send_data(WRONG_NAMESPACE_HEADER)
        await client.on_response
        assert (
            b'<invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_stream_error_missing_to(self, client, server):
        client.send_data(MISSING_TO_HEADER)
        await client.on_response
        assert (
            b'<host-unknown xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_stream_error_unknown_to(self, client, server):
        client.send_data(UNKNOWN_TO_HEADER)
        await client.on_response
        assert (
            b'<host-unknown xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_stream_bad_format(self, client, server):
        # Register Message
        server.stanza_parser.add_class(stanza.Message, lambda stanza: print(stanza))

        # TODO: El test devuelve Exception ignored revisar porque

        client.send_data(STREAM_HEADER)
        await client.on_response
        client.send_data(BAD_FORMAT_MSG)
        await client.on_response
        assert (
            b'<bad-format xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_stream_bad_namespace_prefix(self, client, server):
        client.send_data(BAD_NAMESPACE_HEADER)
        await client.on_response
        assert (
            b'<bad-namespace-prefix xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_stream_bad_namespace_prefix(self, client, server):
        client.send_data(BAD_NAMESPACE_HEADER)
        await client.on_response
        assert (
            b'<bad-namespace-prefix xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

  
    TODO: Implement this in a future P.53 RFC-6120
    @pytest.mark.asyncio
    async def test_conflict(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<conflict xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()
   

    @pytest.mark.asyncio
    async def test_connection_timeout(self, client, server):
        # Set the soft and hard timeout
        server.deadtime_soft_limit = timedelta(seconds=0.1)
        server.deadtime_hard_limit = timedelta(seconds=0.2)

        # Simulate the reception of stream header
        client.send_data(STREAM_HEADER)
        await client.on_close
        await asyncio.sleep(1)
        assert server._state == XMLStreamState.CLOSED

    @pytest.mark.asyncio
    async def test_host_unknown(self, client, server):
        client.send_data(HOST_UNKNOWN_HEADER)
        await client.on_response
        assert (
            b'<host-unknown xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

  
    TODO: Implement this in a future P.56 RFC-6120
    @pytest.mark.asyncio
    async def test_improper_addressing(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<improper-addressing xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()
 

    @pytest.mark.asyncio
    async def test_internal_server_error(self, client, server):
        client.send_data(BAD_VERSION_HEADER)
        await client.on_response
        assert (
            b'<internal-server-error xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()


    TODO: Implement this in a future P.56 RFC-6120
    @pytest.mark.asyncio
    async def test_invalid_from(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<ivalid-from xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()


    @pytest.mark.asyncio
    async def test_invalid_namespace(self, client, server):
        client.send_data(INVALID_NAMESPACE_HEADER)
        await client.on_response
        assert (
            b'<invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    @pytest.mark.asyncio
    async def test_invalid_default_namespace(self, client, server):
        client.send_data(INVALID_DEFAULT_HEADER)
        await client.on_response
        assert (
            b'<invalid-namespace xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.57 RFC-6120
    @pytest.mark.asyncio
    async def test_invalid_xml(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<ivalid-xml xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.58 RFC-6120
    @pytest.mark.asyncio
    async def test_not_authorized(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<not-authorized xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.59 RFC-6120
    @pytest.mark.asyncio
    async def test_not_well_formed(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<not-well-formed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.59 RFC-6120
    @pytest.mark.asyncio
    async def test_policy_violation(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<not-well-formed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.59 RFC-6120
    @pytest.mark.asyncio
    async def test_remote_conection_failed(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<remote-connection-failed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.60 RFC-6120
    @pytest.mark.asyncio
    async def test_reset(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<reset xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.61 RFC-6120
    @pytest.mark.asyncio
    async def test_resource_constraint(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<resource-constraint xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.61 RFC-6120
    @pytest.mark.asyncio
    async def test_restricted_xml(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<restricted-xml xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.61 RFC-6120
    @pytest.mark.asyncio
    async def test_see_other_host(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<see-other-host xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.63 RFC-6120
    @pytest.mark.asyncio
    async def test_shutdown(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<system-shutdown xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()
      @pytest.mark.asyncio
    async def test_unsupported_encoding(self, client, server):
        client.send_data(UNSUPPORTED_ENCODING_HEADER)
        ...
        await client.on_response
        assert (
            b'<unsupported-encoding xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()

    TODO: Implement this in a future P.65 RFC-6120
    @pytest.mark.asyncio
    async def test_unsupported_feature(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<unsupported-feature xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()


    TODO: Implement this in a future P.65 RFC-6120
    @pytest.mark.asyncio
    async def test_unsupported_stanza_type(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<unsupported-stanza-type xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()


    @pytest.mark.asyncio
    async def test_unsupported_version(self, client, server):
        client.send_data(UNSUPPORTED_VERSION_HEADER)
        ...
        await client.on_response
        assert (
            b'<unsupported-version xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()


    TODO: Implement this in a future P.67 RFC-6120
    @pytest.mark.asyncio
    async def test_application_specific(self, client, server):
        client.send_data(STREAM_HEADER)
        ...
        await client.on_response
        assert (
            b'<not-well-formed xmlns="urn:ietf:params:xml:ns:xmpp-streams"/></stream:error>'
            in client._data
        )
        client.close()
    """