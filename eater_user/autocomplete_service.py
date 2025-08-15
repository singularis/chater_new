from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import asyncio
import json
import logging
from common import verify_jwt_token
from postgres import database, autocomplete_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autocomplete Service", version="1.0.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.user_connections = {}

    async def connect(self, websocket: WebSocket, user_email: str):
        self.active_connections.append(websocket)
        self.user_connections[user_email] = websocket
        logger.info(f"User {user_email} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_email: str):
        self.active_connections.remove(websocket)
        if user_email in self.user_connections:
            del self.user_connections[user_email]
        logger.info(f"User {user_email} disconnected from WebSocket")

    async def send_personal_message(self, message: str, user_email: str):
        if user_email in self.user_connections:
            await self.user_connections[user_email].send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup():
    await database.connect()
    logger.info("Database connected")
    logger.info("Autocomplete service ready")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Database disconnected")

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    try:
        # Test database connection
        await database.fetch_one("SELECT 1")
        return {"status": "healthy", "service": "autocomplete-service"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    try:
        # Test database connection and basic functionality
        await database.fetch_one("SELECT 1")
        return {"status": "ready", "service": "autocomplete-service"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.websocket("/ws/autocomplete")
async def websocket_autocomplete(websocket: WebSocket):
    user_email = None
    try:
        # Accept the WebSocket connection first
        await websocket.accept()
        
        # Receive authentication data
        auth_data = await websocket.receive_text()
        auth_message = json.loads(auth_data)
        if auth_message.get("type") != "auth":
            await websocket.send_text(json.dumps({"error": "Authentication required"}))
            await websocket.close()
            return
        token = auth_message.get("token")
        if not token:
            await websocket.send_text(json.dumps({"error": "Token required"}))
            await websocket.close()
            return
        try:
            payload = verify_jwt_token(token)
            user_email = payload.get("sub") or payload.get("email") or payload.get("user_email")
            if not user_email:
                await websocket.send_text(json.dumps({"error": "Invalid token - no email"}))
                await websocket.close()
                return
        except Exception:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await websocket.close()
            return
        
        # Add to connection manager
        await manager.connect(websocket, user_email)
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "user_email": user_email
        }))
        
        # Main message loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                message = json.loads(data)
                if message.get("type") == "search":
                    query = message.get("query", "").strip()
                    limit = min(message.get("limit", 10), 50)
                    if len(query) < 2:
                        await websocket.send_text(json.dumps({
                            "type": "results",
                            "results": [],
                            "query": query,
                            "message": "Query too short"
                        }))
                        continue
                    users = await autocomplete_query(query, limit, user_email)
                    await websocket.send_text(json.dumps({
                        "type": "results",
                        "results": users,
                        "query": query,
                        "count": len(users)
                    }))
                elif message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
    except WebSocketDisconnect:
        if user_email:
            manager.disconnect(websocket, user_email)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if user_email:
            manager.disconnect(websocket, user_email)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 