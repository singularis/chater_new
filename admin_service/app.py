import logging
import os
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

from postgres import get_all_admin_data, get_admin_data_by_user, create_admin_table
from admin_processor import process_admin_messages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize database
try:
    create_admin_table()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


@app.route("/")
def index():
    """Home page showing all admin data."""
    try:
        admin_data = get_all_admin_data()
        
        # HTML template for displaying admin data
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .admin-card {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .admin-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    flex-wrap: wrap;
                }
                .user-email {
                    font-weight: bold;
                    color: #007bff;
                    font-size: 1.1em;
                }
                .date {
                    color: #6c757d;
                    font-size: 0.9em;
                }
                .admin-text {
                    color: #495057;
                    line-height: 1.6;
                    margin-top: 10px;
                    padding: 10px;
                    background-color: white;
                    border-radius: 5px;
                    border-left: 4px solid #007bff;
                }
                .no-admin {
                    text-align: center;
                    color: #6c757d;
                    font-style: italic;
                    padding: 40px;
                }
                .stats {
                    background-color: #e9ecef;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    text-align: center;
                    color: #495057;
                }
                @media (max-width: 768px) {
                    .admin-header {
                        flex-direction: column;
                        align-items: flex-start;
                    }
                    .date {
                        margin-top: 5px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Admin Dashboard</h1>
                
                <div class="stats">
                    <strong>Total Admin Records: {{ total_count }}</strong>
                </div>
                
                {% if admin_data %}
                    {% for admin in admin_data %}
                    <div class="admin-card">
                        <div class="admin-header">
                            <div class="user-email">{{ admin.user_email }}</div>
                            <div class="date">{{ admin.date }}</div>
                        </div>
                        <div class="admin-text">{{ admin.admin_data }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="no-admin">
                        <p>No admin data available yet.</p>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_template, admin_data=admin_data, total_count=len(admin_data))
        
    except Exception as e:
        logger.error(f"Error displaying admin data: {e}")
        return f"Error loading admin data: {str(e)}", 500


@app.route("/api/admin")
def api_admin():
    """API endpoint to get all admin data as JSON."""
    try:
        admin_data = get_all_admin_data()
        return jsonify({
            "success": True,
            "count": len(admin_data),
            "admin_data": admin_data
        })
    except Exception as e:
        logger.error(f"Error getting admin data via API: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/admin/<user_email>")
def api_user_admin(user_email):
    """API endpoint to get admin data for a specific user."""
    try:
        admin_data = get_admin_data_by_user(user_email)
        return jsonify({
            "success": True,
            "user_email": user_email,
            "count": len(admin_data),
            "admin_data": admin_data
        })
    except Exception as e:
        logger.error(f"Error getting admin data for user {user_email}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "admin-service"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Start the admin processor in a background thread
    processor_thread = threading.Thread(target=process_admin_messages, daemon=True)
    processor_thread.start()
    logger.info("Admin processor started in background thread")
    
    logger.info(f"Starting Admin Service on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug) 