from fastapi.websockets import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connected_clients = []

    async def connect(self, websocket: WebSocket):
        client_ip = f"{websocket.client.host}:{websocket.client.port}"
        print(websocket.client)
        print(websocket.headers)

        await websocket.accept()

        self.connected_clients.append(websocket)

        message = {"client": client_ip, "message": f"Welcome {client_ip}"}

        await websocket.send_json(message)

    async def send_message(self, websocket: WebSocket, message: dict):

        await websocket.send_json(message)

    async def disconnect(self, websocket: WebSocket):
        print("disconnecting")
        self.connected_clients.remove(websocket)