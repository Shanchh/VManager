from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from api import auth_handler, user_routes, admin_routes
from websocket_app import websocket_routes

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

app.include_router(admin_routes.app, tags=["AdminApi"])
app.include_router(user_routes.app, tags=["UserApi"])
app.include_router(auth_handler.app, tags=["AuthHandler"])
app.include_router(websocket_routes.app, tags=["WebSocket"])

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=2626, reload=True)