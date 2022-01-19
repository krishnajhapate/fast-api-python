import imp
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from databases import Database
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()

# exception handler for authjwt
# in production, you can tweak performance using orjson response
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# database connection
app = FastAPI()
database = Database("sqlite:///test.db")


@app.on_event("startup")
async def database_connect():
    await database.connect()


@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()


html = ""
with open('index.html', 'r') as f:
    html = f.read()


@app.get("/")
def home():
    return HTMLResponse(html)


@app.post("/test")
async def fetch_data(id: int):
    query = "SELECT * FROM tablename WHERE ID={}".format(str(id))


class ConnectionManager:

    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


@app.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(f"Client {id}:{data}")
