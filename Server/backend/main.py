from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os

from api import auth_handler, user_routes, admin_routes
from websocket_app import websocket_routes
from schedule_event import aps_event

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload
# uvicorn main:app --host 192.168.0.106 --port 2666 --reload

app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/")
async def serve_root():
    return FileResponse("build/index.html")

# 提供其他路径的文件，支持 React 的路由
@app.get("/{path:path}")
async def serve_other_paths(path: str):
    return FileResponse("build/index.html")

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/zip", filename=filename)
    else:
        return {"error": f"File {filename} not found"}

app.include_router(admin_routes.app, tags=["AdminApi"])
app.include_router(user_routes.app, tags=["UserApi"])
app.include_router(auth_handler.app, tags=["AuthHandler"])
app.include_router(websocket_routes.app, tags=["WebSocket"])

scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(aps_event.record_online_users, CronTrigger(minute="*/5", second="0"))

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=2626, reload=True)