import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.telegram_client import start_client, handle_new_message

@pytest.mark.asyncio
@patch("app.telegram_client.storage.save_message", new_callable=AsyncMock)
@patch("app.telegram_client.config.get_channels")
async def test_handle_new_message_saves_message_from_target_channel(
    mock_get_channels, mock_save_message
):
    """
    Tests that handle_new_message correctly processes and saves a message
    when it comes from a channel that is in the configured list.
    """
    # Arrange
    # Configure the mock to return a list of target channels
    mock_get_channels.return_value = ["target_channel_name"]

    # Create a mock event object that simulates a Telethon NewMessage event
    mock_event = MagicMock()
    mock_event.chat.title = "target_channel_name"
    mock_event.chat.id = 12345
    mock_event.message.id = 999
    mock_event.message.text = "Test message body"
    mock_event.message.date = "2023-01-01T12:00:00+00:00"

    # Act
    # Await the handler function with the mock event
    await handle_new_message(mock_event)

    # Assert
    # Check that save_message was called exactly once
    mock_save_message.assert_awaited_once()

    # Check that save_message was called with the correct arguments from the event
    call_args = mock_save_message.call_args[0]
    assert call_args[0] == mock_event.chat.id
    assert call_args[1] == mock_event.chat.title
    assert call_args[2] == mock_event.message.id
    assert call_args[3] == mock_event.message.text
    assert call_args[4] == mock_event.message.date


@pytest.mark.asyncio
@patch("app.telegram_client.storage.save_message", new_callable=AsyncMock)
@patch("app.telegram_client.config.get_channels")
async def test_handle_new_message_ignores_message_from_other_channel(
    mock_get_channels, mock_save_message
):
    """
    Tests that handle_new_message correctly ignores a message
    when it comes from a channel that is NOT in the configured list.
    """
    # Arrange
    # Configure the mock to return a list of target channels
    mock_get_channels.return_value = ["target_channel_name"]

    # Create a mock event from a different, unmonitored channel
    mock_event = MagicMock()
    mock_event.chat.title = "some_other_channel"
    mock_event.chat.id = 54321

    # Act
    await handle_new_message(mock_event)

    # Assert
    # Check that save_message was not called
    mock_save_message.assert_not_awaited() 