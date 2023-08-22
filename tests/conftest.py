import multiprocessing
import pytest
import time

from vangare import VangareServer, run_server


# Fixture to start the server before the tests and stop it after the tests.
@pytest.fixture(scope="session", autouse=True)
def run_server_fixture():
    # Create a server instance and start it in a separate process.
    server = VangareServer(host="0.0.0.0", connection_timeout=3)
    server_process = multiprocessing.Process(
        target=run_server,
        args=(
            server,
            True,
            False
        ),
    )
    server_process.start()

    # Wait for the server to start.
    time.sleep(1)

    # Yield the server instance to the tests.
    yield server_process

    # Stop the server.
    server_process.terminate()
    server_process.join()
