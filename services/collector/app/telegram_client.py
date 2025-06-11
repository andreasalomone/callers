from telethon import TelegramClient, events
from telethon.sessions import StringSession

from . import config, storage

client = TelegramClient(
    StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH
)

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

    print(f"Listening for messages from: {config.CHANNELS}")
    client.run_until_disconnected() 