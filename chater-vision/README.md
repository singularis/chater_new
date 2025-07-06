# Chater Vision Service

Java-based computer vision service providing advanced image analysis, object detection, and visual understanding capabilities for the Chater platform.

## 🎯 Purpose

The Chater Vision Service provides comprehensive computer vision functionality, including:
- Advanced image analysis and object detection
- Food recognition and nutritional analysis
- Scene understanding and description
- Visual content moderation
- Real-time image processing
- Integration with Google Vision API and Gemini models

## 🏗️ Architecture

### Core Components
- **Vision Client**: Google Vision API and Gemini Vision integration
- **Image Processor**: Image preprocessing and optimization
- **Object Detection**: Advanced object recognition and classification
- **Food Analyzer**: Specialized food recognition and nutritional analysis
- **Scene Parser**: Scene understanding and contextual analysis
- **Response Generator**: Structured response generation and formatting

### Dependencies
- **Google Vision API**: Primary computer vision service
- **Google Gemini API**: Advanced vision and reasoning capabilities
- **Apache Kafka**: Message broker for request/response handling
- **Image Processing Libraries**: Java-based image manipulation
- **Machine Learning Models**: Custom and pre-trained models

## 🔧 Configuration

### Environment Variables
```bash
# Google Vision API
VISION_API_KEY=your-vision-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id

# Gemini Integration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_VISION_MODEL=gemini-2.0-flash-exp

# Kafka Configuration
BOOTSTRAP_SERVERS=your-kafka-broker:port
CONSUMER_GROUP=chater-vision-group

# Service Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
MAX_IMAGE_SIZE=10485760

# Processing Configuration
CONCURRENT_REQUESTS=5
BATCH_SIZE=10
IMAGE_QUALITY=HIGH
```

### Kafka Topics
- **Consumes**: `chater-vision` - Image analysis requests
- **Produces**: `gemini-response` - Vision analysis responses

## 🚀 Getting Started

### Prerequisites
- Java 11+
- Google Cloud Project with Vision API enabled
- Service account with Vision API permissions
- Apache Kafka broker
- Maven or Gradle for build management

### Installation
1. **Build the service**
   ```bash
   mvn clean compile package
   ```

2. **Configure Google Cloud credentials**
   ```bash
   # Set service account key
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
   
   # Set project ID
   export GCP_PROJECT_ID=your-project-id
   ```

3. **Configure Kafka**
   ```bash
   export BOOTSTRAP_SERVERS=localhost:9092
   export VISION_API_KEY=your-vision-api-key
   ```

4. **Run the service**
   ```bash
   java -jar target/chater-vision.jar
   ```

### Development Setup
```bash
# Install dependencies
mvn install

# Run in development mode
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

## 📋 Features

### Image Analysis
- **Object Detection**: Identify and classify objects in images
- **Text Recognition**: Extract text from images (OCR)
- **Face Detection**: Detect faces and facial features
- **Landmark Recognition**: Identify famous landmarks
- **Logo Detection**: Recognize brand logos and symbols
- **Label Detection**: Generate descriptive labels for images

### Food Recognition
- **Food Identification**: Identify specific food items
- **Nutritional Analysis**: Estimate nutritional content
- **Portion Estimation**: Estimate serving sizes
- **Ingredient Detection**: Identify food ingredients
- **Meal Classification**: Categorize meals by type
- **Dietary Information**: Detect dietary restrictions and allergens

### Scene Understanding
- **Scene Classification**: Identify scene types and contexts
- **Activity Recognition**: Detect activities and actions
- **Spatial Analysis**: Understand spatial relationships
- **Color Analysis**: Dominant colors and color schemes
- **Composition Analysis**: Image composition and layout
- **Quality Assessment**: Image quality and technical metrics

### Content Moderation
- **Safety Detection**: Identify potentially harmful content
- **Inappropriate Content**: Detect adult or violent content
- **Spam Detection**: Identify spam or promotional content
- **Brand Safety**: Ensure brand-safe content
- **Policy Compliance**: Enforce content policies

## 🔄 Message Processing

### Request Format
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "image_data": "base64-encoded-image",
    "image_url": "https://example.com/image.jpg",
    "analysis_type": "food_recognition",
    "features": [
      "OBJECT_LOCALIZATION",
      "TEXT_DETECTION",
      "LABEL_DETECTION"
    ],
    "max_results": 10,
    "context": "Food photo for nutritional analysis"
  }
}
```

### Response Format
```json
{
  "key": "unique-request-id",
  "value": {
    "analysis_results": {
      "objects": [
        {
          "name": "pizza",
          "confidence": 0.95,
          "bounding_box": {
            "x": 100,
            "y": 150,
            "width": 200,
            "height": 180
          }
        }
      ],
      "labels": [
        {
          "description": "Food",
          "score": 0.98
        }
      ],
      "text": [
        {
          "text": "Menu",
          "confidence": 0.92
        }
      ]
    },
    "food_analysis": {
      "identified_foods": [
        {
          "name": "Margherita Pizza",
          "confidence": 0.89,
          "estimated_calories": 285,
          "portion_size": "1 slice"
        }
      ],
      "nutritional_info": {
        "calories": 285,
        "protein": 12.0,
        "carbs": 36.0,
        "fat": 10.0
      }
    },
    "processing_time": 2.8,
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Processing Flow
1. **Message Consumption**: Receive image analysis requests
2. **Image Validation**: Validate image format and size
3. **Preprocessing**: Optimize image for analysis
4. **Vision API Call**: Send request to Google Vision API
5. **Gemini Enhancement**: Use Gemini for advanced analysis
6. **Results Processing**: Process and structure results
7. **Response Generation**: Generate formatted response
8. **Message Publication**: Send results to Kafka

## 🤖 AI Integration

### Google Vision API Features
```java
public class VisionAnalyzer {
    private final ImageAnnotatorClient visionClient;
    private final GenerativeModel geminiModel;
    
    public VisionAnalysis analyzeImage(byte[] imageData) {
        // Create Vision API request
        Image image = Image.newBuilder()
            .setContent(ByteString.copyFrom(imageData))
            .build();
        
        // Configure features
        Feature objectDetection = Feature.newBuilder()
            .setType(Feature.Type.OBJECT_LOCALIZATION)
            .setMaxResults(10)
            .build();
        
        // Perform analysis
        AnnotateImageRequest request = AnnotateImageRequest.newBuilder()
            .addFeatures(objectDetection)
            .setImage(image)
            .build();
        
        return processVisionResponse(visionClient.batchAnnotateImages(request));
    }
}
```

### Gemini Vision Integration
- **Advanced Scene Understanding**: Detailed scene analysis
- **Contextual Reasoning**: Understanding context and relationships
- **Natural Language Descriptions**: Generate human-like descriptions
- **Multi-modal Analysis**: Combine vision with text understanding
- **Custom Instructions**: Tailored analysis based on specific needs

### Food Recognition Models
- **Custom Food Database**: Extensive food recognition database
- **Nutritional Mapping**: Map foods to nutritional information
- **Portion Estimation**: AI-powered portion size estimation
- **Cultural Cuisine Recognition**: Support for international cuisines
- **Dietary Analysis**: Allergen and dietary restriction detection

## 📊 Monitoring & Metrics

### Performance Metrics
- **Processing Time**: Average image analysis time
- **Accuracy Metrics**: Recognition accuracy rates
- **API Usage**: Vision API call statistics
- **Error Rate**: Failed analysis attempts
- **Throughput**: Images processed per minute

### Quality Metrics
- **Recognition Confidence**: Average confidence scores
- **Food Identification Accuracy**: Food recognition accuracy
- **False Positive Rate**: Incorrect identifications
- **User Satisfaction**: User feedback on accuracy
- **Model Performance**: AI model performance metrics

### Health Monitoring
```java
@Component
public class VisionHealthChecker {
    
    @Scheduled(fixedRate = 60000)
    public void checkServiceHealth() {
        HealthCheck health = new HealthCheck();
        health.visionApiConnectivity = checkVisionAPI();
        health.geminiConnectivity = checkGeminiAPI();
        health.kafkaConnectivity = checkKafkaConnection();
        health.memoryUsage = checkMemoryUsage();
        
        publishHealthMetrics(health);
    }
}
```

## 🔒 Security & Privacy

### Image Security
- **Input Validation**: Strict image format and size validation
- **Malware Scanning**: Check for embedded malware
- **Content Filtering**: Filter inappropriate content
- **Data Sanitization**: Clean metadata and EXIF data
- **Secure Storage**: Temporary secure image storage

### Privacy Protection
- **Data Minimization**: Process only necessary image data
- **Temporary Processing**: Delete images after processing
- **Anonymization**: Remove personally identifiable information
- **Access Control**: Strict access controls and permissions
- **Audit Logging**: Comprehensive processing audit logs

### API Security
- **Authentication**: Secure API key management
- **Rate Limiting**: Prevent abuse and quota exhaustion
- **Request Validation**: Validate all incoming requests
- **Error Handling**: Secure error responses
- **Monitoring**: Real-time security monitoring

## 🐳 Deployment

### Docker
```dockerfile
FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/chater-vision.jar app.jar
COPY service-account.json /app/credentials/
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chater-vision
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chater-vision
  template:
    spec:
      containers:
      - name: chater-vision
        image: your-registry/chater-vision:latest
        env:
        - name: VISION_API_KEY
          valueFrom:
            secretKeyRef:
              name: chater-vision-secrets
              key: VISION_API_KEY
        - name: BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
        - name: GCP_PROJECT_ID
          value: "your-project-id"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: gcp-credentials
          mountPath: /var/secrets/google
          readOnly: true
      volumes:
      - name: gcp-credentials
        secret:
          secretName: gcp-service-account
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
mvn test

# Run with coverage
mvn test jacoco:report
```

### Integration Tests
```bash
# Test Vision API integration
mvn test -Dtest=VisionApiIntegrationTest

# Test Kafka integration
mvn test -Dtest=KafkaIntegrationTest

# Test food recognition
mvn test -Dtest=FoodRecognitionTest
```

### Performance Testing
```bash
# Load test with concurrent requests
mvn test -Dtest=LoadTest -Dconcurrent=5 -Drequests=100

# Image processing performance
mvn test -Dtest=ImageProcessingPerformanceTest
```

### Accuracy Testing
```bash
# Test food recognition accuracy
mvn test -Dtest=FoodRecognitionAccuracyTest

# Test object detection accuracy
mvn test -Dtest=ObjectDetectionAccuracyTest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow Java coding standards
- Add comprehensive error handling
- Include unit tests for new features
- Test image processing thoroughly
- Monitor API usage and costs
- Document new features and APIs
- Consider performance implications for image processing 