import logging
import requests
from flask import jsonify, redirect, url_for, flash

logger = logging.getLogger(__name__)


def eater_admin_request(session):
    """
    Handle eater admin requests - check session authentication and fetch statistics page content
    """
    # Check if user is logged in via session (not token required)
    if "logged_in" not in session:
        logger.warning("Unauthorized eater_admin access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))
    
    try:
        # Fetch content from the local statistics page
        response = requests.get("http://192.168.0.113/statistics", timeout=10)
        response.raise_for_status()
        
        # Return the content with appropriate headers
        return response.text, response.status_code, {'Content-Type': response.headers.get('Content-Type', 'text/html')}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching statistics page: {e}")
        return jsonify({"error": "Failed to fetch statistics data", "details": str(e)}), 500 