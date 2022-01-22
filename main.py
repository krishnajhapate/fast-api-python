import imp
from typing import List, Optional
from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from databases import Database
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from app import models
from app.database import engine

app = FastAPI()
models.Base.metadata.create_all(engine)


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}


@app.get('/partially-protected')
def partially_protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()

    # If no jwt is sent in the request, get_jwt_subject() will return None
    current_user = Authorize.get_jwt_subject() or "anonymous"
    return {"user": current_user}


html = ""
with open('index.html', 'r') as f:
    html = f.read()


@app.get("/chat/{id}")
def home(id: int):
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


@app.websocket("/ws/chat/{id}")
async def websocket_endpoint(websocket: WebSocket, id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(f"Client {id}:{data}")
