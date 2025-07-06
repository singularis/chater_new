# Chater Gemini Service

Google Gemini AI integration service providing advanced multi-modal AI capabilities and conversational intelligence for the Chater platform.

## 🎯 Purpose

The Chater Gemini Service provides Google Gemini AI integration functionality, including:
- Multi-modal AI processing (text, images, audio, video)
- Advanced reasoning and problem-solving capabilities
- Real-time conversation processing
- Context-aware response generation
- Efficient token usage and cost optimization
- Robust error handling and fallback mechanisms

## 🏗️ Architecture

### Core Components
- **Gemini Client**: Google AI API client with authentication
- **Multi-Modal Processor**: Handle text, image, and multimedia inputs
- **Context Manager**: Advanced conversation memory and context handling
- **Response Optimizer**: Response quality and relevance optimization
- **Rate Controller**: Request throttling and quota management
- **Safety Filter**: Content safety and policy enforcement

### Dependencies
- **Google AI API**: Primary Gemini model service
- **Apache Kafka**: Message broker for request/response handling
- **Redis**: Optional caching and session management
- **Google Cloud**: Authentication and additional services

## 🔧 Configuration

### Environment Variables
```bash
# Google AI Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_THINK_MODEL=gemini-2.0-pro-exp
MAX_OUTPUT_TOKENS=8000
TEMPERATURE=0.8

# Kafka Configuration
BOOTSTRAP_SERVER=your-kafka-broker:port
CONSUMER_GROUP=chater-gemini-group

# Service Configuration
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=60

# Safety and Moderation
SAFETY_THRESHOLD=BLOCK_MEDIUM_AND_ABOVE
HARM_CATEGORIES=HARASSMENT,HATE_SPEECH,DANGEROUS_CONTENT

# Performance
CONCURRENT_REQUESTS=5
BATCH_SIZE=10
```

### Kafka Topics
- **Consumes**: `gemini-send` - Chat requests for Gemini processing
- **Produces**: `gemini-response` - Gemini-generated responses

## 🚀 Getting Started

### Prerequisites
- Google AI API key with Gemini access
- Apache Kafka broker
- Python 3.8+ or Docker environment
- Access to required environment variables

### Installation
1. **Install dependencies**
   ```bash
   pip install google-generativeai confluent-kafka python-dotenv pillow
   ```

2. **Configure environment**
   ```bash
   # Set Google AI API key
   export GEMINI_API_KEY=your-api-key
   
   # Set Kafka broker
   export BOOTSTRAP_SERVER=localhost:9092
   
   # Set model configuration
   export GEMINI_MODEL=gemini-2.0-flash-exp
   export GEMINI_THINK_MODEL=gemini-2.0-pro-exp
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

### Multi-Modal Capabilities
- **Text Generation**: Natural language understanding and generation
- **Image Analysis**: Visual understanding and description
- **Video Processing**: Video content analysis and summarization
- **Audio Processing**: Speech recognition and audio understanding
- **Code Generation**: Programming assistance and code completion
- **Mathematical Reasoning**: Advanced mathematical problem solving

### Advanced AI Features
- **Chain of Thought**: Step-by-step reasoning for complex problems
- **Few-shot Learning**: Learning from minimal examples
- **Context Awareness**: Long-term conversation memory
- **Multimodal Reasoning**: Combining text, images, and other modalities
- **Safety Filtering**: Built-in content safety and moderation
- **Factual Grounding**: Accurate and up-to-date information

### Performance Optimization
- **Response Streaming**: Real-time response generation
- **Batch Processing**: Efficient batch request handling
- **Caching**: Intelligent response caching
- **Load Balancing**: Request distribution across instances
- **Token Optimization**: Efficient token usage strategies

## 🔄 Message Processing

### Request Format
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "message": "User's question or prompt",
    "context": "Previous conversation context",
    "model": "gemini-2.0-flash-exp",
    "max_tokens": 2000,
    "temperature": 0.8,
    "system_instruction": "Custom system instructions",
    "media": [
      {
        "type": "image",
        "data": "base64-encoded-image",
        "mime_type": "image/jpeg"
      }
    ],
    "tools": ["code_execution", "web_search"]
  }
}
```

### Response Format
```json
{
  "key": "unique-request-id",
  "value": {
    "response": "Generated AI response",
    "model": "gemini-2.0-flash-exp",
    "usage": {
      "prompt_tokens": 75,
      "completion_tokens": 150,
      "total_tokens": 225
    },
    "finish_reason": "stop",
    "safety_ratings": [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"
      }
    ],
    "citations": [
      {
        "startIndex": 100,
        "endIndex": 150,
        "uri": "https://example.com/source"
      }
    ],
    "timestamp": "2024-01-01T00:00:00Z",
    "processing_time": 3.2
  }
}
```

### Processing Flow
1. **Message Consumption**: Receive requests from Kafka
2. **Input Validation**: Validate request format and media
3. **Safety Check**: Pre-process content for safety
4. **Context Preparation**: Prepare conversation context
5. **API Request**: Send request to Gemini API
6. **Response Processing**: Process and validate response
7. **Safety Filtering**: Post-process for safety compliance
8. **Message Publication**: Send response to Kafka

## 🤖 AI Integration

### Gemini Models
- **Gemini 2.0 Flash**: Fast, efficient processing
- **Gemini 2.0 Pro**: Advanced reasoning and complex tasks
- **Gemini 2.0 Flash Thinking**: Enhanced reasoning capabilities
- **Gemini Vision**: Specialized for image understanding
- **Gemini Code**: Optimized for programming tasks

### Multi-Modal Processing
```python
class MultiModalProcessor:
    def __init__(self):
        self.supported_formats = ['image', 'video', 'audio', 'text']
        self.max_file_size = 20 * 1024 * 1024  # 20MB
    
    def process_media(self, media_data):
        # Validate media format
        # Optimize for processing
        # Extract relevant features
        return processed_media
    
    def generate_response(self, text, media, context):
        # Combine text and media inputs
        # Generate contextual response
        # Apply safety filters
        return ai_response
```

### Safety and Moderation
- **Content Filtering**: Automatic harmful content detection
- **Bias Mitigation**: Reduce potential biases in responses
- **Policy Enforcement**: Comply with AI usage policies
- **User Protection**: Protect users from harmful content
- **Audit Logging**: Track safety-related events

## 📊 Monitoring & Metrics

### Performance Metrics
- **Response Time**: Average and percentile response times
- **Token Usage**: Daily and monthly token consumption
- **Request Rate**: Requests per second/minute/hour
- **Error Rate**: Failed requests and error classifications
- **Multi-modal Usage**: Usage breakdown by media type

### Quality Metrics
- **Response Quality**: User satisfaction and feedback
- **Safety Compliance**: Safety filter effectiveness
- **Accuracy**: Factual accuracy of responses
- **Relevance**: Context relevance scoring
- **Engagement**: User interaction patterns

### Health Monitoring
```python
def health_check():
    checks = {
        "gemini_api": check_gemini_connection(),
        "kafka_broker": check_kafka_connection(),
        "memory_usage": check_memory_usage(),
        "processing_queue": check_queue_depth(),
        "safety_filters": check_safety_system()
    }
    return all(checks.values())
```

## 🔒 Security & Privacy

### API Security
- **API Key Management**: Secure key storage and rotation
- **Request Authentication**: Validate all incoming requests
- **Rate Limiting**: Prevent abuse and quota exhaustion
- **Input Sanitization**: Clean and validate all inputs
- **Audit Logging**: Comprehensive security logging

### Data Privacy
- **Data Minimization**: Process only necessary data
- **Temporary Storage**: Minimize data retention
- **Encryption**: Encrypt data in transit and at rest
- **Access Control**: Strict access controls and permissions
- **Compliance**: GDPR and privacy regulation compliance

### Content Safety
- **Harmful Content Detection**: Automatic detection and blocking
- **Age-Appropriate Content**: Ensure content appropriateness
- **Misinformation Prevention**: Reduce false information
- **Bias Detection**: Monitor and mitigate biases
- **Policy Enforcement**: Enforce platform policies

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
  name: chater-gemini
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chater-gemini
  template:
    spec:
      containers:
      - name: chater-gemini
        image: your-registry/chater-gemini:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chater-gemini-secrets
              key: GEMINI_API_KEY
        - name: BOOTSTRAP_SERVER
          value: "kafka-service:9092"
        - name: GEMINI_MODEL
          value: "gemini-2.0-flash-exp"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### Configuration Management
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: chater-gemini-config
data:
  GEMINI_MODEL: "gemini-2.0-flash-exp"
  GEMINI_THINK_MODEL: "gemini-2.0-pro-exp"
  MAX_OUTPUT_TOKENS: "8000"
  TEMPERATURE: "0.8"
  SAFETY_THRESHOLD: "BLOCK_MEDIUM_AND_ABOVE"
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Run with coverage
python -m pytest tests/unit/ --cov=chater_gemini/
```

### Integration Tests
```bash
# Test Gemini API integration
python -m pytest tests/integration/test_gemini.py

# Test multi-modal processing
python -m pytest tests/integration/test_multimodal.py

# Test safety filters
python -m pytest tests/integration/test_safety.py
```

### Performance Testing
```bash
# Load test with concurrent requests
python tests/load/load_test.py --concurrent=5 --requests=500

# Multi-modal performance test
python tests/performance/multimodal_test.py
```

### Safety Testing
```bash
# Test content safety filters
python tests/safety/safety_test.py

# Test harmful content detection
python tests/safety/harmful_content_test.py
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
- Test multi-modal capabilities thoroughly
- Monitor safety and content policies
- Document API changes and new features 