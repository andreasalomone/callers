import asyncio
import asyncpg
import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .database import get_db, DATABASE_URL

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Pass the manager instance to the listener
    print("Starting up and initializing DB listener...")
    listener_task = asyncio.create_task(db_listener(manager))
    yield
    # Shutdown
    print("Shutting down, cancelling listener task...")
    listener_task.cancel()

app = FastAPI(lifespan=lifespan)

# Instrument the app with Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Configure CORS using an environment variable
# The variable should be a comma-separated string of origins.
# e.g., "http://localhost:3000,https://my-prod-domain.com"
# If the variable is not set, it defaults to an empty list, which is restrictive.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

# For development, if no origins are specified, we can add a default for convenience.
# In a real production environment, CORS_ORIGINS should always be explicitly set.
if not origins and os.getenv("ENVIRONMENT") == "development":
    origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept(subprotocol="json")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

async def db_listener(manager: ConnectionManager):
    """Listens for new message notifications and broadcasts them."""
    conn = None
    while True:
        try:
            if conn is None or conn.is_closed():
                print("Connecting to database for listener...")
                conn = await asyncpg.connect(dsn=DATABASE_URL)
                await conn.add_listener("new_message", notification_handler)
                print("Database listener connected and listening.")

            # The `await` here is important. It allows the loop to yield
            # and prevents it from busy-waiting, while also checking for connection health.
            await conn.fetchval('SELECT 1')
            await asyncio.sleep(5)

        except (asyncpg.exceptions.PostgresConnectionError, OSError) as e:
            print(f"Database listener connection error: {e}. Reconnecting in 5 seconds...")
            if conn and not conn.is_closed():
                await conn.close()
            conn = None
            await asyncio.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred in the DB listener: {e}")
            if conn and not conn.is_closed():
                await conn.close()
            conn = None
            await asyncio.sleep(10)

async def notification_handler(connection, pid, channel, payload):
    """Handles the notification from PostgreSQL."""
    print(f"Received notification: {payload}")
    message_id = int(payload)
    
    # Need a new session to fetch the message
    async for db in get_db():
        message = await crud.get_message(db, message_id=message_id)
        if message:
            # Pydantic model to dict, then to JSON string
            message_schema = schemas.Message.from_orm(message)
            message_json = message_schema.model_dump_json()
            await manager.broadcast(message_json)

@app.get("/healthz", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.get("/api/feed", response_model=list[schemas.Message])
async def read_messages(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    messages = await crud.get_messages(db, skip=skip, limit=limit)
    return messages

async def client_listener(websocket: WebSocket):
    """Listens for messages from the client to detect disconnection."""
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # This exception is expected when the client closes the connection.
        pass

async def server_pinger(websocket: WebSocket):
    """Sends a ping to the client every 20 seconds to keep the connection alive."""
    while True:
        try:
            await asyncio.sleep(20)
            # The subprotocol negotiation ensures the client should understand this.
            await websocket.send_json({"type": "ping"})
        except (WebSocketDisconnect, asyncio.CancelledError):
            # Stop pinging if the client disconnects or the task is cancelled.
            break
        except Exception as e:
            print(f"Error in WebSocket pinger: {e}")
            break

@app.websocket("/api/feed/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Run listener and pinger concurrently
    listener_task = asyncio.create_task(client_listener(websocket))
    pinger_task = asyncio.create_task(server_pinger(websocket))
    
    # Wait for either task to complete (which signals a disconnect or error)
    done, pending = await asyncio.wait(
        [listener_task, pinger_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Clean up pending tasks to prevent them from running forever
    for task in pending:
        task.cancel()

    manager.disconnect(websocket)
    print("Client disconnected, cleaned up tasks.") 