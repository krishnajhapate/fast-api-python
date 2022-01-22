from typing import List
from fastapi import FastAPI, WebSocket, status, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app import models, oauth2
from app import schemas
from app.database import engine, get_db
from sqlalchemy.orm import Session
from app.hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm
import json

app = FastAPI()
models.Base.metadata.create_all(engine)


class Token(BaseModel):
    access_token: str
    token_type: str


@app.get('/', tags=['User'], response_model=schemas.User)
def user_info(db: Session = Depends(get_db),
              current_user: schemas.User = Depends(oauth2.get_current_user)):
    user = db.query(
        models.Users).filter(models.Users.email == current_user).first()
    return user


@app.post(
    '/login',
    tags=["User"],
    status_code=201,
)
def login(request: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(
        models.Users).filter(models.Users.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")
    access_token = oauth2.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "bearer": "bearer"}


@app.post('/register', tags=["User"], status_code=201)
def register(request: schemas.Register, db: Session = Depends(get_db)):
    create_user = models.Users(name=request.name,
                               email=request.email,
                               password=Hash.get_password_hash(
                                   request.password))
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    return create_user


html = ""
with open('index.html', 'r') as f:
    html = f.read()


@app.get("/chat", tags=["chat"])
def chat():
    login_html = ''
    with open('login.html', 'r') as f:
        login_html = f.read()
    return HTMLResponse(login_html)


@app.get("/chat/{id}", tags=['Chat'])
def home(id: int):
    return HTMLResponse(html)


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
async def websocket_endpoint(websocket: WebSocket, id: int, token: str):
    await manager.connect(websocket)
    if not token:
        # if Hash.verify
        data = await websocket.receive_text()
        await manager.broadcast("Not authorised")

    while True:
        data = await websocket.receive_text()
        user = oauth2.verify_token(token)
        print(user)
        await manager.broadcast(json.dumps({"user": user, "message": data}))
