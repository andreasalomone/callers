import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Now we can import the handler function directly
from app.telegram_client import handle_new_message

@pytest.mark.asyncio
@patch("app.telegram_client.storage.save_message", new_callable=AsyncMock)
@patch("app.telegram_client.config.get_channels")
async def test_handle_new_message_saves_from_target_channel(mock_get_channels, mock_save_message):
    """
    Tests that handle_new_message saves a message from a monitored channel.
    """
    # Arrange
    mock_get_channels.return_value = ["target_channel_name", "12345"]
    mock_event = MagicMock()
    mock_event.chat.title = "target_channel_name"
    mock_event.chat.id = 12345
    mock_event.message.id = 999
    mock_event.message.text = "Test message body"
    mock_event.message.date = "2023-01-01T12:00:00+00:00"

    # Act
    await handle_new_message(mock_event)

    # Assert
    mock_save_message.assert_awaited_once_with(
        channel_id=12345,
        channel_name="target_channel_name",
        message_id=999,
        body="Test message body",
        created_at="2023-01-01T12:00:00+00:00",
    )

@pytest.mark.asyncio
@patch("app.telegram_client.storage.save_message", new_callable=AsyncMock)
@patch("app.telegram_client.config.get_channels")
async def test_handle_new_message_ignores_other_channel(mock_get_channels, mock_save_message):
    """
    Tests that handle_new_message ignores a message from an unmonitored channel.
    """
    # Arrange
    mock_get_channels.return_value = ["target_channel_name"]
    mock_event = MagicMock()
    mock_event.chat.title = "some_other_channel"
    mock_event.chat.id = 54321

    # Act
    await handle_new_message(mock_event)

    # Assert
    mock_save_message.assert_not_awaited()

@pytest.mark.asyncio
@patch("app.telegram_client.storage.save_message", new_callable=AsyncMock)
async def test_handle_new_message_ignores_events_without_chat(mock_save_message):
    """
    Tests that the handler gracefully ignores events that don't have a chat attribute.
    """
    # Arrange
    mock_event = MagicMock()
    # Remove the 'chat' attribute to simulate an event we can't process
    del mock_event.chat

    # Act
    await handle_new_message(mock_event)

    # Assert
    mock_save_message.assert_not_awaited() 