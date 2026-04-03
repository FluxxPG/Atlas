from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.manager import realtime_manager

router = APIRouter()


@router.websocket("/ws/platform")
async def platform_ws(websocket: WebSocket):
    channel = "platform"
    await realtime_manager.subscribe(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await realtime_manager.unsubscribe(channel, websocket)

