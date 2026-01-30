import json
import time
import os
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import threading
import base64
from openai import OpenAI
from socket_manager import WebSocketManager

# uvicorn ai_server:AI --ws-ping-timeout 600

client = OpenAI(base_url="http://localhost:8080/v1")

character_messages = []

AI = FastAPI()

AI.waiting = False

manager = WebSocketManager()


@AI.post("/character")
def character(prompt: str, img=None):
    while AI.waiting:
        time.sleep(1)
    AI.waiting = True
    new_message = []

    context = [
        {
            "role": "system",
            "content": """
            You ara an anime catgirl. \
            You respond in a sweet and cheerful manner. \
            You end your sentences with 'nya' or other cat sounds."""
        }
    ]
    if type(img) is str and os.path.isfile(img):
        print("image received")
        base64_image = encode_image(img)
        new_message = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt},
                            {"type": "img_url", "img_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]
            }
        ]
    else:
        character_messages.append({"role": "user", "content": prompt})
    print(context+character_messages+new_message)

    completion = client.chat.completions.create(
        model="model",
        messages=context+character_messages+new_message
    )

    print(completion.choices[0].message.content)
    text = completion.choices[0].message.content

    if type(img) is str and os.path.isfile(img):
        character_messages.append({'role': 'user', 'content': prompt})

    character_messages.append({"role": "assistant", "content": text})

    with open("character_chat.txt", "a") as file:
        try:
            file.write(f"\nuser: {prompt}\nassistant: {text}")
        except:
            pass
    while len(character_messages) > 40:
        del character_messages[0]
    AI.waiting = False

    return text


@AI.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    while True:
        try:
            message = await websocket.receive_json()
            print(message["prompt"])
            if message["function"] == "character":
                if "img" in message.keys():
                    response = character(message["prompt"], message["img"])
                else:
                    response = character(message["prompt"])
                await websocket.send_json({"message": response})
        except WebSocketDisconnect:
            await manager.disconnect(websocket)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")