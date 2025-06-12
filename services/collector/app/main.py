import asyncio
from app import storage, telegram_client

async def main():
    print("Setting up database...")
    await storage.setup_database()
    print("Database setup complete.")

    await telegram_client.start_client()
    
    # Keep the main coroutine alive to allow the client to run in the background.
    print("Collector is running. Press Ctrl+C to stop.")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Collector shutting down.")

if __name__ == "__main__":
    asyncio.run(main()) 