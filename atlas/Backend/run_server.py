# backend/run_server.py
import asyncio
import websockets
from backend.notifier import clients

async def handler(websocket):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

def run_server():
    loop = asyncio.get_event_loop()
    loop.create_task(websockets.serve(handler, "localhost", 6789))

def run_server_in_background():
    import threading
    threading.Thread(target=run_server, daemon=True).start()