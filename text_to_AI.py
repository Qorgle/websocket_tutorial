import websocket
import asyncio
import json
import threading


def on_message(wsapp, message):
    received = json.loads(message)
    print(received["message"])


def run_websocket():
    wsapp.run_forever()


def main():
    socket_thread = threading.Thread(target=run_websocket, args=())
    socket_thread.start()
    while True:
        prompt = input("prompt: ")
        prompt_json = json.dumps({"function": "character", "prompt": prompt})
        wsapp.send(prompt_json)


if __name__ == "__main__":
    header = {"user": "app"}
    wsapp = websocket.WebSocketApp(
        "ws://localhost:8000/ws",
        on_message=on_message,
        header=header
    )
    main()
