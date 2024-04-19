import json

from fastapi import APIRouter
from starlette.responses import FileResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
# from api.chat.utils import ws_manager

# router = APIRouter(
#     prefix="/chat",
#     tags=["Chat"]
# )
#
# @router.get("/")
# async def get():
#     return FileResponse("templates/chat/index.html")
#
#
# @router.websocket("/ws/{chat_id}")
# async def websocket_endpoint(websocket: WebSocket):
#     try:
#         await websocket.accept()
#         new_one = json.loads(await websocket.receive_text())
#         await ws_manager.connect(new_one, websocket)
#         while True:
#             data = json.loads(await websocket.receive_text())
#             await ws_manager.send_message(data)
#     except WebSocketDisconnect:
#         ws_manager.disconnect(websocket)
