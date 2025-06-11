import asyncio
import asyncpg
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .database import get_db, DATABASE_URL

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

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
        await websocket.accept()
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

@app.on_event("startup")
async def startup_event():
    # Pass the manager instance to the listener
    asyncio.create_task(db_listener(manager))

@app.get("/api/feed", response_model=list[schemas.Message])
async def read_messages(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    messages = await crud.get_messages(db, skip=skip, limit=limit)
    return messages

@app.websocket("/api/feed/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected.") 