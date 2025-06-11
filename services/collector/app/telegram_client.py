from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest

from . import config, storage

client = TelegramClient(
    StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH
)

async def fetch_and_save_history(channel, limit=50):
    """Fetches the recent message history of a channel and saves it."""
    print(f"Fetching message history for {channel}...")
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=limit,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    if not history.messages:
        print(f"No message history found for {channel}.")
        return

    print(f"Found {len(history.messages)} messages in {channel}.")
    for message in history.messages:
        # Skip empty messages
        if not message.text:
            continue
        
        # Use the channel entity from the message if available
        channel_entity = message.chat if hasattr(message, 'chat') else await client.get_entity(message.peer_id)

        storage.save_message(
            channel_id=channel_entity.id,
            channel_name=channel_entity.title,
            message_id=message.id,
            body=message.text,
            created_at=message.date,
        )
    print(f"Finished saving history for {channel}.")


def start_client():
    """Starts the telethon client and adds the new message event handler."""
    
    @client.on(events.NewMessage(chats=config.CHANNELS))
    async def handle_new_message(event):
        """This function is called whenever a new message is received."""
        print(f"New message from channel {event.chat.title}")
        
        storage.save_message(
            channel_id=event.chat.id,
            channel_name=event.chat.title,
            message_id=event.message.id,
            body=event.message.text,
            created_at=event.message.date,
        )

    print("Starting Telethon client...")
    client.start()
    print("Client started.")
    
    # Generate and print session string if it's not already set
    if not config.SESSION_STRING:
        session_string = client.session.save()
        print("\nYour session string is:\n")
        print(session_string)
        print("\nPlease set it as the SESSION_STRING environment variable and restart.")
        # We don't run forever in this case, so the user can copy the string
        return

    # Fetch history before starting the event loop
    async def initial_fetch():
        print("Performing initial fetch of message history...")
        for channel in config.CHANNELS:
            await fetch_and_save_history(channel)
        print("Initial fetch complete.")

    client.loop.run_until_complete(initial_fetch())

    print(f"Listening for messages from: {config.CHANNELS}")
    client.run_until_disconnected() 