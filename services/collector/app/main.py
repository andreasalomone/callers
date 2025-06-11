from app import storage, telegram_client

def main():
    print("Setting up database...")
    storage.setup_database()
    print("Database setup complete.")

    telegram_client.start_client()

if __name__ == "__main__":
    main() 