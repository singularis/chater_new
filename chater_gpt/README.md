# Chater GPT Service

OpenAI GPT integration service providing advanced language model capabilities and conversational AI for the Chater platform.

## 🎯 Purpose

The Chater GPT Service provides OpenAI integration functionality, including:
- GPT model integration and response generation
- Conversation context management
- Multi-modal capabilities with vision support
- Rate limiting and request optimization
- Error handling and fallback mechanisms
- Token usage tracking and optimization

## 🏗️ Architecture

### Core Components
- **GPT Client**: OpenAI API client with authentication
- **Context Manager**: Conversation history and context handling
- **Message Processor**: Kafka message consumption and processing
- **Response Generator**: AI response generation and formatting
- **Rate Limiter**: Request throttling and quota management
- **Error Handler**: Robust error handling and recovery

### Dependencies
- **OpenAI API**: Primary language model service
- **Apache Kafka**: Message broker for request/response handling
- **Redis**: Optional caching for responses and context
- **Logging Framework**: Comprehensive logging and monitoring

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
MODEL=gpt-4o-mini
VISION_MODEL=gpt-4o-latest
MAX_TOKENS=4000
TEMPERATURE=0.7

# Kafka Configuration
BOOTSTRAP_SERVER=your-kafka-broker:port
CONSUMER_GROUP=chater-gpt-group

# Service Configuration
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30

# Rate Limiting
REQUESTS_PER_MINUTE=60
DAILY_TOKEN_LIMIT=1000000
```

### Kafka Topics
- **Consumes**: `gpt-send` - Chat requests for GPT processing
- **Produces**: `gpt-response` - GPT-generated responses

## 🚀 Getting Started

### Prerequisites
- OpenAI API key with appropriate permissions
- Apache Kafka broker
- Python 3.8+ or Docker environment
- Access to required environment variables

### Installation
1. **Install dependencies**
   ```bash
   pip install openai confluent-kafka python-dotenv
   ```

2. **Configure environment**
   ```bash
   # Set OpenAI API key
   export OPENAI_API_KEY=your-api-key
   
   # Set Kafka broker
   export BOOTSTRAP_SERVER=localhost:9092
   
   # Set model configuration
   export MODEL=gpt-4o-mini
   export VISION_MODEL=gpt-4o-latest
   ```

3. **Run the service**
   ```bash
   python main.py
   ```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run in development mode
export LOG_LEVEL=DEBUG
python main.py
```

## 📋 Features

### Language Model Capabilities
- **Text Generation**: High-quality text responses
- **Conversation Context**: Multi-turn conversation support
- **Vision Processing**: Image analysis and understanding
- **Code Generation**: Programming assistance and code completion
- **Multi-language Support**: Support for multiple languages
- **Custom Instructions**: System prompts and behavior customization

### Message Processing
- **Async Processing**: Non-blocking message handling
- **Batch Processing**: Efficient batch request handling
- **Priority Queue**: Request prioritization
- **Retry Logic**: Automatic retry on failures
- **Circuit Breaker**: Failure protection mechanisms

### Performance Optimization
- **Response Caching**: Cache frequently requested responses
- **Context Compression**: Optimize conversation context
- **Token Management**: Efficient token usage tracking
- **Request Batching**: Batch similar requests
- **Load Balancing**: Distribute requests across instances

## 🔄 Message Processing

### Request Format
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "message": "User's question or prompt",
    "context": "Previous conversation context",
    "model": "gpt-4o-mini",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "Custom system instructions",
    "images": ["base64-encoded-image"]
  }
}
```

### Response Format
```json
{
  "key": "unique-request-id",
  "value": {
    "response": "Generated AI response",
    "model": "gpt-4o-mini",
    "usage": {
      "prompt_tokens": 50,
      "completion_tokens": 100,
      "total_tokens": 150
    },
    "finish_reason": "stop",
    "timestamp": "2024-01-01T00:00:00Z",
    "processing_time": 2.5
  }
}
```

### Processing Flow
1. **Message Consumption**: Receive requests from Kafka
2. **Input Validation**: Validate request format and parameters
3. **Context Preparation**: Prepare conversation context
4. **API Request**: Send request to OpenAI API
5. **Response Processing**: Process and format response
6. **Message Publication**: Send response to Kafka
7. **Usage Tracking**: Log token usage and metrics

## 🤖 AI Integration

### OpenAI Models
- **GPT-4o Mini**: Fast, cost-effective text generation
- **GPT-4o**: Advanced reasoning and complex tasks
- **GPT-4o Latest**: Latest model with enhanced capabilities
- **Vision Models**: Image analysis and understanding
- **Custom Models**: Fine-tuned models for specific use cases

### Conversation Management
```python
class ConversationManager:
    def __init__(self):
        self.context_window = 8000
        self.max_history = 10
    
    def prepare_context(self, user_message, history):
        # Prepare conversation context
        # Manage token limits
        # Optimize for relevance
        return formatted_context
    
    def update_history(self, user_message, ai_response):
        # Update conversation history
        # Maintain context relevance
        # Prune old messages if needed
```

### Error Handling
- **API Rate Limits**: Graceful handling of rate limit errors
- **Network Errors**: Retry logic for network failures
- **Invalid Requests**: Proper error responses for bad requests
- **Token Limits**: Handle context window overflow
- **Service Downtime**: Fallback mechanisms during outages

## 📊 Monitoring & Metrics

### Performance Metrics
- **Response Time**: Average and percentile response times
- **Token Usage**: Daily and monthly token consumption
- **Request Rate**: Requests per second/minute/hour
- **Error Rate**: Failed requests and error types
- **Queue Depth**: Kafka consumer lag

### Business Metrics
- **User Engagement**: Messages per user
- **Model Performance**: User satisfaction scores
- **Cost Tracking**: API usage costs
- **Feature Usage**: Vision vs text processing
- **Conversation Length**: Average conversation turns

### Health Monitoring
```python
def health_check():
    checks = {
        "openai_api": check_openai_connection(),
        "kafka_broker": check_kafka_connection(),
        "memory_usage": check_memory_usage(),
        "queue_depth": check_queue_depth()
    }
    return all(checks.values())
```

## 🔒 Security & Privacy

### API Security
- **API Key Management**: Secure key storage and rotation
- **Request Validation**: Input sanitization and validation
- **Rate Limiting**: Prevent abuse and quota exhaustion
- **Audit Logging**: Track all API interactions
- **Error Sanitization**: Prevent information leakage

### Data Privacy
- **Data Minimization**: Process only necessary data
- **Context Cleanup**: Regular context history cleanup
- **PII Protection**: Detect and handle personal information
- **Retention Policies**: Automatic data deletion
- **Compliance**: GDPR and privacy regulation compliance

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chater-gpt
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chater-gpt
  template:
    spec:
      containers:
      - name: chater-gpt
        image: your-registry/chater-gpt:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chater-gpt-secrets
              key: OPENAI_API_KEY
        - name: BOOTSTRAP_SERVER
          value: "kafka-service:9092"
        - name: MODEL
          value: "gpt-4o-mini"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Custom Kubernetes Operator
The service can be deployed using the custom Kubernetes operator:
```yaml
apiVersion: chater.example.com/v1
kind: ChaterGpt
metadata:
  name: chater-gpt-instance
spec:
  namespace: chater-gpt
  bootstrapServer: "kafka-service:9092"
  model: "gpt-4o-mini"
  visionModel: "gpt-4o-latest"
  replicas: 3
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Run with coverage
python -m pytest tests/unit/ --cov=chater_gpt/
```

### Integration Tests
```bash
# Test OpenAI integration
python -m pytest tests/integration/test_openai.py

# Test Kafka integration
python -m pytest tests/integration/test_kafka.py
```

### Load Testing
```bash
# Load test with multiple concurrent requests
python tests/load/load_test.py --concurrent=10 --requests=1000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow Python coding standards (PEP 8)
- Add comprehensive error handling
- Include unit tests for new features
- Document API changes
- Monitor token usage and costs 