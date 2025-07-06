# Admin Service

Administrative backend service for the Chater platform, handling feedback processing, database management, and system monitoring.

## 🎯 Purpose

The Admin Service provides administrative functionality for the Chater platform, including:
- Processing user feedback messages from Kafka
- Managing database operations and administration
- System health monitoring and metrics
- Background task processing

## 🏗️ Architecture

### Core Components
- **Flask Application**: RESTful API endpoints for admin operations
- **Feedback Processor**: Kafka consumer for processing user feedback
- **Database Layer**: PostgreSQL connection and data management
- **Health Monitoring**: Service health checks and metrics

### Dependencies
- **Apache Kafka**: Message broker for feedback processing
- **PostgreSQL**: Database for storing feedback and admin data
- **Redis**: Optional caching layer

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
POSTGRES_HOST=your-database-host
POSTGRES_DB=your-database-name
POSTGRES_USER=your-database-user
POSTGRES_PASSWORD=your-database-password
DB_PORT=5432

# Message Broker
BOOTSTRAP_SERVER=your-kafka-broker:port

# Service Configuration
PORT=5000
FLASK_DEBUG=false
```

### Kafka Topics
- **Consumes**: `feedback` - User feedback messages
- **Produces**: None (data stored in database)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Apache Kafka broker
- Access to required environment variables

### Installation
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Set environment variables
   export POSTGRES_HOST=localhost
   export POSTGRES_DB=chater_admin
   export BOOTSTRAP_SERVER=localhost:9092
   ```

3. **Run the service**
   ```bash
   python app.py
   ```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_DEBUG=true
python app.py
```

## 📋 API Endpoints

### Health Check
- **GET** `/health` - Service health status
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00",
    "service": "admin-service"
  }
  ```

### Feedback Management
- **GET** `/feedback` - List all feedback entries
- **GET** `/feedback/{id}` - Get specific feedback entry
- **POST** `/feedback` - Create new feedback entry
- **PUT** `/feedback/{id}` - Update feedback entry
- **DELETE** `/feedback/{id}` - Delete feedback entry

## 🔄 Background Processing

### Feedback Processor
The service runs a background thread that continuously processes feedback messages from Kafka:

```python
def process_feedback_messages():
    """Main processor to consume feedback messages and write to database."""
    # Creates consumer for 'feedback' topic
    # Processes messages and stores in PostgreSQL
    # Commits messages after successful processing
```

### Message Format
Expected feedback message structure:
```json
{
  "value": {
    "time": "2024-01-01T00:00:00",
    "user_email": "user@example.com",
    "feedback": "User feedback text"
  }
}
```

## 🗄️ Database Schema

### Feedback Table
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    feedback_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);
```

## 🔒 Security

### Authentication
- Service-to-service authentication via internal network
- Database connections use encrypted credentials
- Environment variables for sensitive configuration

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Error handling without data exposure

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: admin-service
  template:
    spec:
      containers:
      - name: admin-service
        image: your-registry/admin-service:latest
        ports:
        - containerPort: 5000
        env:
        - name: POSTGRES_HOST
          value: "your-database-host"
        - name: BOOTSTRAP_SERVER
          value: "your-kafka-broker:port"
```

## 📊 Monitoring

### Metrics
- Service health status
- Feedback processing rate
- Database connection status
- Kafka consumer lag

### Logging
- Structured logging with configurable levels
- Request/response logging
- Error tracking and alerting
- Performance metrics

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Run with coverage
python -m pytest tests/unit/ --cov=.
```

### Integration Tests
```bash
# Run integration tests (requires database and Kafka)
python -m pytest tests/integration/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

 