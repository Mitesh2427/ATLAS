# backend/notifier.py
import asyncio
import json

clients = set()

async def notify_all(alert_data):
    if clients:
        message = json.dumps(alert_data)
        await asyncio.gather(*[client.send(message) for client in clients])

def notify_alert(module, message, level="info"):
    alert_data = {
        "module": module,
        "message": message,
        "level": level
    }
    loop = asyncio.get_event_loop()
    loop.create_task(notify_all(alert_data))
