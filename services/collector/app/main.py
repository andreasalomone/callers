import asyncio
from app import storage, telegram_client

async def main():
    print("Setting up database...")
    await storage.setup_database()
    print("Database setup complete.")

    telegram_client.start_client()

if __name__ == "__main__":
    asyncio.run(main()) 