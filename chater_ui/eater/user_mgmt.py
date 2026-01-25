import logging
import os
import requests
from flask import jsonify

logger = logging.getLogger(__name__)

# Default to internal k8s service name in chater-ui namespace
AUTOCOMPLETE_SERVICE_URL = os.getenv("AUTOCOMPLETE_SERVICE_URL", "http://eater-users-service")

def update_user_nickname(request, user_email):
    """
    Proxy the nickname update request to the eater_user/autocomplete service.
    """
    try:
        # validate request
        data = request.get_json()
        if not data or "nickname" not in data:
             return jsonify({"error": "Nickname is required"}), 400
        
        nickname = data["nickname"]
        
        # Call internal service
        url = f"{AUTOCOMPLETE_SERVICE_URL}/autocomplete/update_nickname"
        headers = {
            # Use the same token or just trust internal network? 
            # The backend service expects @token_required wrapper which checks 'Authorization' header.
            # So we must forward the Authorization header.
            "Authorization": request.headers.get("Authorization"),
            "Content-Type": "application/json"
        }
        
        # We need to send valid JSON that matches what update_nickname_endpoint expects
        payload = {"nickname": nickname}
        
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if resp.status_code == 200:
             return jsonify(resp.json()), 200
        else:
             logger.error(f"Failed to update nickname: {resp.status_code} {resp.text}")
             try:
                 return jsonify(resp.json()), resp.status_code
             except:
                 return jsonify({"error": "Failed to update nickname"}), resp.status_code

    except Exception as e:
        logger.exception(f"Error updating nickname for {user_email}: {e}")
        return jsonify({"error": "Internal Error"}), 500
