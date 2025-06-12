import pytest
from fastapi.testclient import TestClient
import asyncio

from app.main import app

# Use the regular TestClient for WebSockets
client = TestClient(app)

def test_websocket_connection():
    """
    Tests that a client can successfully connect to the WebSocket endpoint.
    """
    with client.websocket_connect("/api/feed/stream", subprotocols=["json"]) as websocket:
        # The connection should be accepted, so no exception should be raised here.
        assert websocket

def test_websocket_receives_ping():
    """
    Tests that the server sends a ping to the client to keep the connection alive.
    We reduce the sleep time in the pinger for the test to run faster.
    """
    # This is a bit of a trick to speed up the test. We'll temporarily
    # patch the sleep duration in the server_pinger task.
    # A more complex setup might involve dependency injection for the pinger's config.
    from app import main
    original_sleep = asyncio.sleep
    main.asyncio.sleep = lambda t: original_sleep(t / 20) # Speed up 20s sleep to 1s

    try:
        with client.websocket_connect("/api/feed/stream", subprotocols=["json"]) as websocket:
            # Wait for the ping message from the server
            data = websocket.receive_json()
            assert data == {"type": "ping"}
    finally:
        # Restore the original sleep function to avoid side effects on other tests
        main.asyncio.sleep = original_sleep 