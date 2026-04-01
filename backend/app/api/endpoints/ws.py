from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.core.config import settings
from app.schemas.token import TokenPayload
from app.services.websocket import manager

router = APIRouter()

async def get_token_user_id(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
        return token_data.sub
    except JWTError:
        return None

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id = await get_token_user_id(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # We just need it open to push data, so we wait for any messages to keep it alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
