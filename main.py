from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import random
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

settings = {
	"auto": True,
	"pump": False,
	"light": False,
	"lighting_start": "23:00",
	"lighting_end": "05:00",
	"watering_time": 15
}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
	return templates.TemplateResponse(request=request, name="index.html")

def get_sensors_data():
	return random.choice([{
		"temp": 100,
		"humidity": 60,
		"co2": 400,
		"nutrient": 80,
		"ph": 6.5,
		"ec": 1.5,
		"temp_solution": 20,
		"watering_start": "08:00",
		"watering_end": "8:15",
		"settings": settings
	},
	{
		"temp": 20,
		"humidity": 80,
		"co2": 204,
		"nutrient": 23,
		"ph": 1.7,
		"ec": 9.7,
		"temp_solution": 57,
		"watering_start": "12:30",
		"watering_end": "15:45",
		"settings": settings
	},
	{
		"temp": 9999,
		"humidity": 70,
		"co2": 289,
		"nutrient": 99,
		"ph": 0.5,
		"ec": 10.6,
		"temp_solution": -820,
		"watering_start": "23:00",
		"watering_end": "8:15",
		"settings": settings
	},
	{
		"temp": 17,
		"humidity": 30,
		"co2": 404,
		"nutrient": 23,
		"ph": 8.7,
		"ec": 3.5,
		"temp_solution": 54,
		"watering_start": "12:02",
		"watering_end": "8:15",
		"settings": settings
	}])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	try:
		while True:
			response = get_sensors_data()
			await websocket.send_text(json.dumps(response))
			await asyncio.sleep(1)
	except WebSocketDisconnect:
		print("WebSocket disconnected")
	except Exception as e:
		print(f"Error: {e}")

@app.post("/toggle-device")
async def toggle_device(request: Request):
	data = await request.json()
	device = data.get("device")
	status = ""
	msg = ""
	try:
		msg = "off" if settings[device] else "on"
		print(device, msg)
		settings[device] = not settings[device]
		status = "success"
	except Exception as e:
		status = "error"
		msg = e
	finally:
		return JSONResponse(content={"status": status, "device": device, "msg": msg})

@app.post("/settings-update")
async def settings_update(request: Request):
	global settings
	data = await request.json()
	settings = data.get("settings")
	print(settings)
	return JSONResponse(content={"status": "success", "msg": "Settings updated"})

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
