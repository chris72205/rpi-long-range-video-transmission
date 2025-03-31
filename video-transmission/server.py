import asyncio
import base64
import io
import time
from aiohttp import web
from picamera2 import Picamera2
from PIL import Image
from pathlib import Path
import json

picam2 = Picamera2()

def create_camera_config(width, height):
    return picam2.create_still_configuration(
        main={"size": (width, height)},
        controls={
            "FrameDurationLimits": (33333, 33333),
            "ExposureTime": 50000,
            "AnalogueGain": 2.0,
        }
    )

# Initialize with default size
camera_config = create_camera_config(2048, 1536)
picam2.configure(camera_config)
picam2.start()

connected_clients = set()

async def index(request):
    return web.FileResponse(Path(__file__).parent / "index.html")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    connected_clients.add(ws)
    print("Client connected")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    if data.get('type') == 'set_size':
                        width = int(data['width'])
                        height = int(data['height'])
                        global camera_config
                        camera_config = create_camera_config(width, height)
                        picam2.stop()
                        picam2.configure(camera_config)
                        picam2.start()
                        print(f"Camera resolution changed to {width}x{height}")
                        # Send resolution info after change
                        await ws.send_json({
                            'type': 'resolution_info',
                            'width': width,
                            'height': height
                        })
                except Exception as e:
                    print(f"Error processing message: {e}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.discard(ws)
        print("Client disconnected")

    return ws

def current_milliseconds():
    return time.time() * 1000

async def broadcast_frames():
    iterations = 0
    jpeg_quality = 50 # reduce quality for faster processing
    buffer = io.BytesIO()
    last_resolution_info = 0

    while True:
        try:
            start_time = current_milliseconds()
            
            # Send resolution info every 5 seconds
            if start_time - last_resolution_info > 5000:
                resolution_info = {
                    'type': 'resolution_info',
                    'width': camera_config['main']['size'][0],
                    'height': camera_config['main']['size'][1]
                }
                if connected_clients:
                    await asyncio.gather(
                        *[ws.send_json(resolution_info) for ws in connected_clients],
                        return_exceptions=True
                    )
                last_resolution_info = start_time
            
            frame = picam2.capture_array()
            
            img = Image.fromarray(frame).rotate(180)
            
            buffer.seek(0)
            buffer.truncate()
            img.save(buffer, format='JPEG', quality=jpeg_quality, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{encoded}"

            if connected_clients:
                await asyncio.gather(
                    *[ws.send_str(data_uri) for ws in connected_clients],
                    return_exceptions=True
                )
                
                connected_clients.difference_update(
                    {ws for ws in connected_clients if ws.closed}
                )

            end_time = current_milliseconds()
            if iterations % 10 == 0:
                print(f"Frame {iterations} processed in {end_time - start_time}ms")
            iterations += 1

            await asyncio.sleep(0.01) 
        except Exception as e:
            print(f"Error in frame loop: {e}")
            await asyncio.sleep(1)

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)


async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Server started on http://0.0.0.0:8080")

    await broadcast_frames()

if __name__ == "__main__":
    asyncio.run(main())