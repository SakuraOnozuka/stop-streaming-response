import datetime
import json
import threading
from pathlib import Path
from typing import Optional
from starlette.middleware.cors import CORSMiddleware # 追加
import cv2
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import subprocess
import time

from time_keeper import TimeKeeperThread, TimeKeeperProcess


app = FastAPI()
video_capture = cv2.VideoCapture(0)

# CORSを回避するために追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

save_dir = Path(__file__).parent.parent.joinpath("images").resolve()
save_dir.mkdir(exist_ok=True)

time_keeper_thread = None
time_keeper_process = None

front_ws: Optional[WebSocket] = None


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

@app.on_event("shutdown")
def shutdown_event():
    global time_keeper_thread, time_keeper_process
    if isinstance(time_keeper_thread, TimeKeeperThread):
        time_keeper_thread.terminate()
    if isinstance(time_keeper_process, TimeKeeperProcess):
        time_keeper_process.terminate()

    if time_keeper_thread is not None:
        time_keeper_thread.join()
        time_keeper_thread = None
        print("killed time keeper")

    if time_keeper_process is not None:
        time_keeper_process.join()
        time_keeper_process = None
        print("killed time keeper")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    print(round(process_time * 1000), "ms")
    # response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/shot")
def shot():
    _, frame = video_capture.read()
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    image_path = str(save_dir.joinpath(time_stamp + ".jpg"))
    cv2.imwrite(image_path, frame)
    return {"image_path": image_path}


def generate() -> bytes:
    while True:
        _, frame = video_capture.read()
        flag, encodedImage = cv2.imencode(".jpg", frame)
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
        print("#", end="")


@app.get("/video_feed")
def video_feed():
    print("jj")
    return StreamingResponse(content=generate(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/ws_test")
async def ws_test():
    result = {"msg": "test", "time": datetime.datetime.now()}
    # WSを用いてフロントに結果を送信
    await front_ws.send_json(json.dumps(result, default=str, ensure_ascii=False))


# WebSockets用のエンドポイント
@app.websocket("/ws_connect")
async def websocket_connect(ws: WebSocket):
    global front_ws
    await ws.accept()
    front_ws = ws
    try:
        while True:
            # # クライアントからメッセージを受信という形でソケットの監視
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws.close()
        # 接続が切れた場合、当該クライアントを削除する
        del front_ws
        print("ws closed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=9001)
