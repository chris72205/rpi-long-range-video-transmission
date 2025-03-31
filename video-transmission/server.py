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

# Debug mode settings
DEBUG_MODE = False
DEBUG_QUALITY = 30  # Lower JPEG quality for debug mode
DEBUG_WIDTH = 640   # Smaller size for debug mode
DEBUG_HEIGHT = 480  # 4:3 aspect ratio

def create_initial_config(width, height, exposure_time=50000, analogue_gain=2.0):
    config = picam2.create_still_configuration(
        main={"size": (width, height)},
        controls={
            "ExposureTime": exposure_time,
            "AnalogueGain": analogue_gain,
        }
    )
    print("Initial camera config:")
    print(f"  Size: {config['main']['size']}")
    print(f"  Controls: {config['controls']}")
    return config

# Initialize with default settings
camera_config = create_initial_config(2048, 1536)
picam2.configure(camera_config)
picam2.start()

connected_clients = set()

async def index(request):
    return web.FileResponse(Path(__file__).parent / "index.html")

async def websocket_handler(request):
    global camera_config, DEBUG_MODE
    
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    connected_clients.add(ws)
    print("Client connected")

    # Send initial camera settings to the new client
    settings_info = {
        'type': 'camera_settings',
        'width': camera_config['main']['size'][0],
        'height': camera_config['main']['size'][1],
        'exposure_time': camera_config['controls']['ExposureTime'],
        'analogue_gain': camera_config['controls']['AnalogueGain'],
        'debug_mode': DEBUG_MODE
    }
    await ws.send_json(settings_info)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    if data.get('type') == 'set_size':
                        width = int(data['width'])
                        height = int(data['height'])
                        print("Updating camera size:")
                        print(f"  Current size: {camera_config['main']['size']}")
                        print(f"  New size: ({width}, {height})")
                        
                        # Update size in current config
                        camera_config['main']['size'] = (width, height)
                        picam2.stop()
                        picam2.configure(camera_config)
                        picam2.start()
                        
                        print(f"Camera resolution changed to {width}x{height}")
                        # Send camera settings after change
                        await ws.send_json({
                            'type': 'camera_settings',
                            'width': width,
                            'height': height,
                            'exposure_time': camera_config['controls']['ExposureTime'],
                            'analogue_gain': camera_config['controls']['AnalogueGain'],
                            'debug_mode': DEBUG_MODE
                        })
                    elif data.get('type') == 'set_exposure':
                        exposure_time = int(data['exposure_time'])
                        print("Updating exposure time:")
                        print(f"  Current exposure: {camera_config['controls']['ExposureTime']}")
                        print(f"  New exposure: {exposure_time}")
                        
                        # Update exposure in current config
                        camera_config['controls']['ExposureTime'] = exposure_time
                        picam2.stop()
                        picam2.configure(camera_config)
                        picam2.start()
                        
                        print(f"Exposure time changed to {exposure_time}μs")
                        # Send camera settings after change
                        await ws.send_json({
                            'type': 'camera_settings',
                            'width': camera_config['main']['size'][0],
                            'height': camera_config['main']['size'][1],
                            'exposure_time': exposure_time,
                            'analogue_gain': camera_config['controls']['AnalogueGain'],
                            'debug_mode': DEBUG_MODE
                        })
                    elif data.get('type') == 'set_gain':
                        analogue_gain = float(data['analogue_gain'])
                        print("Updating analogue gain:")
                        print(f"  Current gain: {camera_config['controls']['AnalogueGain']}")
                        print(f"  New gain: {analogue_gain}")
                        
                        # Update gain in current config
                        camera_config['controls']['AnalogueGain'] = analogue_gain
                        picam2.stop()
                        picam2.configure(camera_config)
                        picam2.start()
                        
                        print(f"Analogue gain changed to {analogue_gain}")
                        # Send camera settings after change
                        await ws.send_json({
                            'type': 'camera_settings',
                            'width': camera_config['main']['size'][0],
                            'height': camera_config['main']['size'][1],
                            'exposure_time': camera_config['controls']['ExposureTime'],
                            'analogue_gain': analogue_gain,
                            'debug_mode': DEBUG_MODE
                        })
                    elif data.get('type') == 'toggle_debug':
                        DEBUG_MODE = not DEBUG_MODE
                        print(f"Debug mode {'enabled' if DEBUG_MODE else 'disabled'}")
                        # Send updated debug mode state
                        await ws.send_json({
                            'type': 'camera_settings',
                            'width': camera_config['main']['size'][0],
                            'height': camera_config['main']['size'][1],
                            'exposure_time': camera_config['controls']['ExposureTime'],
                            'analogue_gain': camera_config['controls']['AnalogueGain'],
                            'debug_mode': DEBUG_MODE
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
            
            # Send camera settings every 5 seconds
            if start_time - last_resolution_info > 5000:
                settings_info = {
                    'type': 'camera_settings',
                    'width': camera_config['main']['size'][0],
                    'height': camera_config['main']['size'][1],
                    'exposure_time': camera_config['controls']['ExposureTime'],
                    'analogue_gain': camera_config['controls']['AnalogueGain'],
                    'debug_mode': DEBUG_MODE
                }
                if connected_clients:
                    await asyncio.gather(
                        *[ws.send_json(settings_info) for ws in connected_clients],
                        return_exceptions=True
                    )
                last_resolution_info = start_time
            
            frame = picam2.capture_array()
            
            img = Image.fromarray(frame).rotate(180)
            
            # In debug mode, resize the image to a smaller size
            if DEBUG_MODE:
                img = img.resize((DEBUG_WIDTH, DEBUG_HEIGHT), Image.Resampling.LANCZOS)
            
            buffer.seek(0)
            buffer.truncate()
            # Use different quality settings based on debug mode
            img.save(buffer, format='JPEG', 
                    quality=DEBUG_QUALITY if DEBUG_MODE else jpeg_quality, 
                    optimize=True)
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