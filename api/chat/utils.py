from typing import List, Dict

from starlette.websockets import WebSocket


class WsManager:
    def __init__(self):
        self.active_connections: List[Dict] = []

    async def connect(self, data: dict, websocket: WebSocket):
        self.active_connections.append({websocket: data})
        print(self.active_connections, end="\n")

    def disconnect(self, websocket: WebSocket):
        print(self.active_connections)
        for i in range(len(self.active_connections)):
            for socket in self.active_connections[i].keys():
                if socket == websocket:
                    self.active_connections.remove(self.active_connections[i])
                    return

    async def send_message(self, data: dict):
        for i in range(len(self.active_connections)):
            for socket, info in self.active_connections[i].items():
                if info["chat_id"] == data["chat_id"]:
                    await socket.send_text(f"{data['name']}: {data['message']}")


ws_manager = WsManager()