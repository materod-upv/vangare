import asyncio
import pytest

from unittest.mock import Mock

from vangare.network.StreamAlivenessMonitor import StreamAlivenessMonitor

@pytest.mark.asyncio
async def test_timeout():

    mock_callback = Mock()

    monitor = StreamAlivenessMonitor(timeout=2, callback=mock_callback)
    monitor.reset() # Start the monitor

    # Reset the monitor before the timeout
    await asyncio.sleep(1)
    monitor.reset()
    await asyncio.sleep(1)
    mock_callback.assert_not_called()

    # Wait the timeout
    await asyncio.sleep(2)
    mock_callback.assert_called_once()

    # Clean the test tasks
    pending_tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    for task in pending_tasks:
        task.cancel()
    await asyncio.wait(pending_tasks)
    