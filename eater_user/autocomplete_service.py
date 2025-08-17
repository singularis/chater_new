from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends
from fastapi.responses import Response
import uvicorn
import asyncio
import json
from starlette.websockets import WebSocketState
from common import get_current_user, validate_websocket_token
from postgres import database, autocomplete_query
from neo4j_connection import neo4j_connection
from proto import add_friend_pb2

app = FastAPI(title="Autocomplete Service", version="1.0.0")

async def safe_send_websocket_message(websocket: WebSocket, message: dict) -> bool:
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(message))
            return True
        return False
    except:
        return False

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.user_connections = {}

    async def connect(self, websocket: WebSocket, user_email: str):
        self.active_connections.append(websocket)
        self.user_connections[user_email] = websocket

    def disconnect(self, websocket: WebSocket, user_email: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_email in self.user_connections:
            del self.user_connections[user_email]

    async def send_personal_message(self, message: str, user_email: str):
        if user_email in self.user_connections:
            await self.user_connections[user_email].send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    await database.connect()
    neo4j_connection.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    neo4j_connection.close()

@app.get("/health")
async def health_check():
    try:
        await database.fetch_one("SELECT 1")
        return {"status": "healthy", "service": "autocomplete-service"}
    except:
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/ready")
async def readiness_check():
    try:
        await database.fetch_one("SELECT 1")
        return {"status": "ready", "service": "autocomplete-service"}
    except:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.post("/autocomplete/addfriend", responses={200: {"content": {"application/x-protobuf": {}}}})
async def add_friend_endpoint(request: Request, user_email: str = Depends(get_current_user)):
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Request body required")
        
        try:
            add_friend_request = add_friend_pb2.AddFriendRequest()
            add_friend_request.ParseFromString(body)
        except:
            raise HTTPException(status_code=400, detail="Invalid protobuf format")
        
        friend_email = add_friend_request.email.strip()
        if not friend_email:
            raise HTTPException(status_code=400, detail="Friend email is required")
        
        if friend_email == user_email:
            raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")
        
        friendship_exists = neo4j_connection.check_friendship_exists(user_email, friend_email)
        if friendship_exists:
            response = add_friend_pb2.AddFriendResponse()
            response.success = True
            return Response(content=response.SerializeToString(), media_type="application/x-protobuf")
        
        success = neo4j_connection.add_friend_relationship(user_email, friend_email)
        response = add_friend_pb2.AddFriendResponse()
        response.success = success
        
        return Response(content=response.SerializeToString(), media_type="application/x-protobuf")
        
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/autocomplete")
async def websocket_autocomplete(websocket: WebSocket):
    user_email = None
    try:
        await websocket.accept()
        
        auth_data = await websocket.receive_text()
        user_email = await validate_websocket_token(websocket, auth_data)
        if not user_email:
            return
        
        await manager.connect(websocket, user_email)
        connection_success = await safe_send_websocket_message(websocket, {
            "type": "connection",
            "status": "connected",
            "user_email": user_email
        })
        if not connection_success:
            return
        
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                if not data.strip():
                    continue
                    
                try:
                    message = json.loads(data)
                except:
                    await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
                    continue
                    
                if message.get("type") == "search":
                    query = message.get("query", "").strip()
                    limit = min(message.get("limit", 10), 50)
                    if len(query) < 2:
                        response = {
                            "type": "results",
                            "results": [],
                            "query": query,
                            "message": "Query too short"
                        }
                        if not await safe_send_websocket_message(websocket, response):
                            break
                        continue
                        
                    try:
                        users = await autocomplete_query(query, limit, user_email)
                        response = {
                            "type": "results",
                            "results": users,
                            "query": query,
                            "count": len(users)
                        }
                        if not await safe_send_websocket_message(websocket, response):
                            break
                    except:
                        if not await safe_send_websocket_message(websocket, {
                            "type": "error",
                            "message": "Database query failed"
                        }):
                            break
                        
                elif message.get("type") == "ping":
                    if not await safe_send_websocket_message(websocket, {"type": "pong"}):
                        break
                    
            except asyncio.TimeoutError:
                if not await safe_send_websocket_message(websocket, {"type": "ping"}):
                    break
            except Exception as e:
                error_str = str(e)
                if "(1001," in error_str or "WebSocket connection is closed" in error_str:
                    break
                
                if not await safe_send_websocket_message(websocket, {
                    "type": "error",
                    "message": "Message processing failed"
                }):
                    break
    except WebSocketDisconnect:
        if user_email:
            manager.disconnect(websocket, user_email)
    except:
        if user_email:
            manager.disconnect(websocket, user_email)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)