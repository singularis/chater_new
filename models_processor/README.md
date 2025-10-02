# Models Processor Service

Local LLM integration service providing self-hosted AI model processing using Ollama for the Chater platform.

## 🎯 Purpose

The Models Processor Service provides local AI model integration functionality, including:
- Self-hosted LLM processing using Ollama
- Privacy-focused local model inference
- Cost-effective AI processing alternative
- Photo analysis with vision-capable local models
- Text generation with open-source models
- Offline AI capabilities

## 🏗️ Architecture

### Core Components
- **Ollama Client**: Integration with Ollama API for local model inference
- **Models Processor**: Main processor orchestrating Kafka consumption and model calls
- **Kafka Consumer**: Message broker integration for request handling
- **Flask Health Server**: HTTP endpoints for health and readiness checks
- **Message Sanitizer**: Output validation and JSON extraction

### Dependencies
- **Ollama**: Local LLM runtime for model inference
- **Apache Kafka**: Message broker for request/response handling
- **Flask**: Lightweight web framework for health endpoints
- **Python Libraries**: confluent-kafka, requests

## 🔧 Configuration

### Environment Variables
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llava:latest
OLLAMA_REQUEST_TIMEOUT=60
OLLAMA_HEALTH_TIMEOUT=5

# Kafka Configuration
BOOTSTRAP_SERVER=your-kafka-broker:port
LOCAL_MODEL_KAFKA_TOPIC=eater-send-photo
CONSUMER_GROUP=models-processor-group

# Service Configuration
EXPECTED_USER_EMAIL=optional-email-filter@example.com
LOG_LEVEL=INFO
PORT=5000

# Performance
CONCURRENT_REQUESTS=5
BATCH_SIZE=10
```

### Kafka Topics
- **Consumes**: `eater-send-photo` - Photo analysis and text generation requests
- **Produces**: `photo-analysis-response` - Vision analysis results
- **Produces**: `gemini-response` - Text generation results

## 🚀 Getting Started

### Prerequisites
- Ollama installed and running locally
- Supported Ollama models pulled (e.g., `llava`, `llama3`, `mistral`)
- Apache Kafka broker
- Python 3.8+ environment

### Ollama Setup
1. **Install Ollama**
   ```bash
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # macOS
   brew install ollama
   ```

2. **Pull required models**
   ```bash
   # Vision model for photo analysis
   ollama pull llava:latest
   
   # Or other vision models
   ollama pull llava:13b
   ollama pull bakllava
   
   # Text models
   ollama pull llama3:latest
   ollama pull mistral:latest
   ```

3. **Start Ollama service**
   ```bash
   ollama serve
   ```

### Service Installation
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Set Ollama endpoint
   export OLLAMA_HOST=http://localhost:11434
   
   # Set model to use
   export OLLAMA_MODEL=llava:latest
   
   # Set Kafka broker
   export BOOTSTRAP_SERVER=localhost:9092
   
   # Set topic to consume
   export LOCAL_MODEL_KAFKA_TOPIC=eater-send-photo
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

### Local Model Capabilities
- **Vision Understanding**: Photo analysis with vision-capable models (LLaVA, BakLLaVA)
- **Text Generation**: Natural language generation with open-source LLMs
- **Food Recognition**: Identify food items from images locally
- **Nutritional Analysis**: Extract nutritional information from photos
- **Privacy-First**: All processing happens locally, no data leaves your infrastructure
- **Cost-Effective**: No API costs, unlimited processing

### Supported Models
- **Vision Models**:
  - `llava:latest` - General vision understanding
  - `llava:13b` - Larger, more accurate vision model
  - `bakllava` - Mistral-based vision model
  
- **Text Models**:
  - `llama3:latest` - Meta's Llama 3 model
  - `mistral:latest` - Mistral AI model
  - `codellama` - Code generation
  - `phi3` - Small, efficient model

### Performance Optimization
- **Request Timeout Management**: Configurable timeouts for model inference
- **Health Monitoring**: Regular model availability checks
- **Response Sanitization**: Clean JSON extraction from model outputs
- **Error Recovery**: Graceful handling of model failures
- **Background Processing**: Non-blocking Kafka message consumption

## 🔄 Message Processing

### Request Format
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "prompt": "Analyze this food image and provide nutritional information",
    "photo": "base64-encoded-image-data"
  }
}
```

### Response Format
**For Photo Analysis:**
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "analysis": "{\"dish_name\":\"Pizza\",\"estimated_avg_calories\":285,\"ingredients\":[\"cheese\",\"tomato sauce\",\"dough\"],\"total_avg_weight\":200,\"contains\":{\"protein\":12.0,\"carbs\":36.0,\"fat\":10.0}}"
  }
}
```

**For Text Generation:**
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "response": "Generated text response from the model",
    "model": "llama3:latest"
  }
}
```

### Processing Flow
1. **Message Consumption**: Receive requests from Kafka topic
2. **User Validation**: Optional email-based filtering
3. **Input Type Detection**: Determine if photo or text request
4. **Model Inference**: Call Ollama API with appropriate model
5. **Response Sanitization**: Extract and validate JSON from model output
6. **Target Topic Selection**: Route to appropriate Kafka topic
7. **Message Publication**: Send results back to Kafka
8. **Commit Offset**: Acknowledge message processing

## 🤖 AI Integration

### Ollama Client Implementation
```python
class OllamaClient:
    def __init__(self, host, model, request_timeout, health_timeout):
        self.host = host
        self.model = model
        self.request_timeout = request_timeout
        self.health_timeout = health_timeout
    
    def analyze_photo_with_ollama(self, prompt, photo_base64):
        # Send vision request to Ollama
        # Returns structured JSON analysis
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "images": [photo_base64],
                "stream": False
            },
            timeout=self.request_timeout
        )
        return response.json()["response"]
    
    def analyze_text_with_ollama(self, message_dict):
        # Send text generation request
        # Returns model response
        prompt = message_dict.get("prompt", message_dict.get("message", ""))
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=self.request_timeout
        )
        return response.json()["response"]
    
    def assert_model_running(self):
        # Check if model is loaded and ready
        response = requests.get(
            f"{self.host}/api/tags",
            timeout=self.health_timeout
        )
        models = response.json().get("models", [])
        if not any(m["name"] == self.model for m in models):
            raise ModelNotRunningError(f"Model {self.model} not available")
```

### Response Sanitization
Models sometimes wrap JSON in code blocks or add explanatory text. The sanitizer:
- Extracts JSON from markdown code blocks
- Validates JSON structure
- Preserves formatting for downstream consumers
- Handles malformed responses gracefully

### Model Selection Guidelines
- **Food Analysis**: Use `llava:13b` or `bakllava` for best accuracy
- **Quick Processing**: Use `llava:latest` for faster response times
- **Text Generation**: Use `llama3:latest` for conversational responses
- **Code Tasks**: Use `codellama` for programming assistance
- **Resource Constrained**: Use `phi3` for lightweight deployments

## 📊 Monitoring & Metrics

### Health Checks
- **GET** `/health` - Service and model health status
  ```json
  {
    "status": "ok",
    "model": "llava:latest"
  }
  ```

- **GET** `/ready` - Readiness probe
  ```json
  {
    "status": "ready",
    "topic": "eater-send-photo"
  }
  ```

### Performance Metrics
- **Inference Time**: Model processing duration
- **Queue Depth**: Kafka consumer lag
- **Success Rate**: Successful vs failed inferences
- **Model Availability**: Ollama service uptime
- **Memory Usage**: Process memory consumption

### Model Performance
- **Throughput**: Images/text processed per minute
- **Accuracy**: Model prediction quality
- **Response Quality**: Structured output compliance
- **Error Rate**: Failed or malformed responses
- **Timeout Rate**: Requests exceeding timeout threshold

## 🔒 Security & Privacy

### Data Privacy
- **Local Processing**: All data stays within your infrastructure
- **No External Calls**: Zero data sent to external APIs
- **User Data Protection**: Email filtering for multi-tenant scenarios
- **Temporary Storage**: No persistent storage of input data
- **GDPR Compliant**: Local processing ensures data sovereignty

### Service Security
- **Input Validation**: Validate message format and content
- **Resource Limits**: Timeout protection against hanging requests
- **Error Sanitization**: Prevent information leakage in errors
- **Access Control**: Kubernetes network policies
- **Audit Logging**: Comprehensive processing logs

### Model Security
- **Model Verification**: Ensure correct model is loaded
- **Resource Monitoring**: Prevent resource exhaustion
- **Crash Recovery**: Automatic service restart on failures
- **Rate Limiting**: Prevent abuse through message throttling

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Start Ollama and the service
EXPOSE 5000
CMD ["sh", "-c", "ollama serve & python main.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: models-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: models-processor
  template:
    spec:
      containers:
      - name: models-processor
        image: your-registry/models-processor:latest
        env:
        - name: OLLAMA_HOST
          value: "http://localhost:11434"
        - name: OLLAMA_MODEL
          value: "llava:latest"
        - name: BOOTSTRAP_SERVER
          value: "kafka-service:9092"
        - name: LOCAL_MODEL_KAFKA_TOPIC
          value: "eater-send-photo"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1  # Optional GPU support
          limits:
            memory: "8Gi"
            cpu: "4000m"
            nvidia.com/gpu: 1
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Sidecar Pattern (Recommended)
```yaml
# Run Ollama as sidecar container
spec:
  containers:
  - name: models-processor
    image: your-registry/models-processor:latest
    # ... processor config
  - name: ollama
    image: ollama/ollama:latest
    ports:
    - containerPort: 11434
    volumeMounts:
    - name: ollama-models
      mountPath: /root/.ollama
  volumes:
  - name: ollama-models
    persistentVolumeClaim:
      claimName: ollama-models-pvc
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Run with coverage
python -m pytest tests/unit/ --cov=models_processor/
```

### Integration Tests
```bash
# Test Ollama integration
python -m pytest tests/integration/test_ollama.py

# Test Kafka integration
python -m pytest tests/integration/test_kafka.py

# Test end-to-end flow
python -m pytest tests/integration/test_e2e.py
```

### Model Testing
```bash
# Test vision model accuracy
python tests/models/test_vision.py

# Test text generation quality
python tests/models/test_text.py

# Benchmark model performance
python tests/performance/benchmark.py
```

### Manual Testing
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Test model inference
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llava:latest","prompt":"Describe this image","images":["base64-image"]}'

# Test health endpoint
curl http://localhost:5000/health
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
- Test with multiple Ollama models
- Monitor resource usage and performance
- Document new features and configurations

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Available Models](https://ollama.com/library)
- [Model Cards](https://ollama.com/library) - Model specifications and capabilities
- [LLaVA Paper](https://arxiv.org/abs/2304.08485) - Vision-language model architecture
- [Llama 3 Model Card](https://ai.meta.com/llama/) - Meta's latest LLM

## 🔍 Troubleshooting

### Common Issues

**Model Not Found**
```bash
# Pull the required model
ollama pull llava:latest
```

**Ollama Not Running**
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

**Slow Inference**
- Use smaller models: `llava:7b` instead of `llava:13b`
- Enable GPU support if available
- Reduce image resolution before sending
- Adjust request timeout values

**Memory Issues**
- Use lighter models: `phi3`, `llama3:8b`
- Reduce concurrent processing
- Monitor container memory limits
- Consider model quantization

**Connection Timeout**
- Increase `OLLAMA_REQUEST_TIMEOUT`
- Check Ollama service logs
- Verify network connectivity
- Monitor Kafka consumer lag

