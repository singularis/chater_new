import asyncio
import json
import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import Response
from starlette.websockets import WebSocketState

from common import token_required, validate_websocket_token
from neo4j_connection import neo4j_connection
from postgres import database, autocomplete_query, get_food_record_by_time
from proto import add_friend_pb2, get_friends_pb2, share_food_pb2
from kafka_producer import produce_message
import uvicorn

app = FastAPI(title="Autocomplete Service", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autocomplete_service")

async def safe_send_websocket_message(websocket: WebSocket, message: dict) -> bool:
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(message))
            return True
        return False
    except Exception:
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
    except Exception:
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/ready")
async def readiness_check():
    try:
        await database.fetch_one("SELECT 1")
        return {"status": "ready", "service": "autocomplete-service"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.post("/autocomplete/addfriend", responses={200: {"content": {"application/x-protobuf": {}}}})
@token_required
async def add_friend_endpoint(request: Request, user_email: str):
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
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/autocomplete/getfriend", responses={200: {"content": {"application/x-protobuf": {}}}})
@token_required
async def get_friends_endpoint(request: Request, user_email: str):
    try:
        friends_list = neo4j_connection.get_user_friends(user_email)
        
        response = get_friends_pb2.GetFriendsResponse()
        response.count = len(friends_list)
        
        for friend_email in friends_list:
            friend = response.friends.add()
            friend.email = friend_email
        
        return Response(content=response.SerializeToString(), media_type="application/x-protobuf")
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/autocomplete/sharefood", responses={200: {"content": {"application/x-protobuf": {}}}})
@token_required
async def share_food_endpoint(request: Request, user_email: str):
    try:
        logger.info(f"/autocomplete/sharefood: start for user={user_email}")
        body = await request.body()
        if not body:
            logger.warning("/autocomplete/sharefood: empty body")
            raise HTTPException(status_code=400, detail="Request body required")

        try:
            share_request = share_food_pb2.ShareFoodRequest()
            share_request.ParseFromString(body)
        except:
            logger.exception("/autocomplete/sharefood: failed to parse protobuf body")
            raise HTTPException(status_code=400, detail="Invalid protobuf format")

        time_value = int(share_request.time)
        from_email = share_request.from_email.strip()
        to_email = share_request.to_email.strip()
        percentage = int(share_request.percentage)
        logger.info("/autocomplete/sharefood: parsed request")

        if not from_email or not to_email:
            logger.warning("/autocomplete/sharefood: missing from_email or to_email")
            raise HTTPException(status_code=400, detail="Both from_email and to_email are required")
        if from_email != user_email:
            logger.warning(f"/autocomplete/sharefood: from_email != token user ({from_email} != {user_email})")
            raise HTTPException(status_code=403, detail="Cannot share food for another user")
        if percentage <= 0 or percentage >= 100:
            logger.warning(f"/autocomplete/sharefood: invalid percentage={percentage}")
            raise HTTPException(status_code=400, detail="percentage must be between 1 and 99")

        # Fetch original food record
        food_record = await get_food_record_by_time(time_value, from_email)
        if not food_record:
            logger.warning(f"/autocomplete/sharefood: food record not found time={time_value} user={from_email}")
            raise HTTPException(status_code=404, detail="Food record not found")
        # Found source record

        # Build message for friend (to_email)
        friend_factor = percentage / 100.0
        raw_contains = food_record.get("contains")
        parsed_contains = {}
        if isinstance(raw_contains, dict):
            parsed_contains = raw_contains
        elif isinstance(raw_contains, str):
            try:
                parsed_contains = json.loads(raw_contains)
            except Exception:
                logger.warning("/autocomplete/sharefood: failed to json-parse 'contains' string; using empty dict")
                parsed_contains = {}
        else:
            parsed_contains = {}

        # Scale only top-level numeric values
        scaled_contains = {}
        for key, value in parsed_contains.items():
            if isinstance(value, (int, float)):
                scaled_contains[key] = value * friend_factor
            else:
                scaled_contains[key] = value

        friend_message = {
            "type": "food_processing",
            "dish_name": food_record["dish_name"],
            "estimated_avg_calories": int(food_record["estimated_avg_calories"] * friend_factor),
            "ingredients": food_record["ingredients"],
            "total_avg_weight": int(food_record["total_avg_weight"] * friend_factor),
            "contains": scaled_contains,
        }
        friend_payload = {
            "key": str(uuid.uuid4()),
            "value": {
                "type": "food_processing",
                "user_email": to_email,
                "analysis": json.dumps(friend_message),
            },
        }
        # Send friend payload
        produce_message(topic="photo-analysis-response", message=friend_payload)

        # Modify original record after sending friend message
        remaining_percentage = 100 - percentage
        modify_payload = {
            "key": str(uuid.uuid4()),
            "value": {
                "user_email": from_email,
                "time": time_value,
                "percentage": remaining_percentage,
            },
        }
        # Send modify payload for remaining percentage
        produce_message(topic="modify_food_record", message=modify_payload)

        response = share_food_pb2.ShareFoodResponse()
        response.success = True
        logger.info("/autocomplete/sharefood: success")
        return Response(content=response.SerializeToString(), media_type="application/x-protobuf")
    except HTTPException:
        raise
    except Exception:
        logger.exception("/autocomplete/sharefood: unexpected error")
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