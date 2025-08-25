# Eater Service

Food tracking and nutritional analysis service for the Chater platform, providing AI-powered food recognition and health insights.

## 🎯 Purpose

The Eater Service provides comprehensive food tracking functionality, including:
- AI-powered food recognition from photos
- Nutritional analysis and calorie tracking
- Meal history and data visualization
- Personalized recommendations
- Weight tracking and health metrics
- Alcohol consumption tracking and summaries
- Integration with vision processing services

## 🏗️ Architecture

### Core Components
- **Food Recognition**: AI-powered image analysis for food identification
- **Nutritional Database**: Comprehensive food and nutrition data
- **Recommendation Engine**: Personalized meal suggestions
- **Data Analytics**: Food intake analysis and trends
- **Database Integration**: PostgreSQL for persistent storage
- **API Gateway**: RESTful endpoints for food operations

### Dependencies
- **Apache Kafka**: Message broker for AI service communication
- **PostgreSQL**: Primary database for food and user data
- **chater-vision**: Computer vision service for image processing
- **Redis**: Caching layer for performance optimization
- **Protocol Buffers**: Efficient data serialization

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
POSTGRES_HOST=your-database-host
POSTGRES_DB=your-database-name
POSTGRES_USER=your-database-user
POSTGRES_PASSWORD=your-database-password

# Message Broker
BOOTSTRAP_SERVER=your-kafka-broker:port

# Service Configuration
EATER_SECRET_KEY=your-secret-key
API_PORT=8080

# AI Integration
VISION_SERVICE_URL=your-vision-service-url
NUTRITION_API_KEY=your-nutrition-api-key
```

### Kafka Topics
- **Produces**: `photo-analysis-request`, `get-recommendations`
- **Consumes**: `photo-analysis-response-check`, `send_today_data`, `delete_food_response`, `send_alcohol_latest`, `send_alcohol_range`

## 🚀 Getting Started

### Prerequisites
- PostgreSQL database
- Apache Kafka broker
- Access to vision processing service
- Python 3.8+ (for Python components)

### Installation
1. **Set up database**
   ```sql
   CREATE DATABASE eater_db;
   CREATE USER eater_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE eater_db TO eater_user;
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_DB=eater_db
   export BOOTSTRAP_SERVER=localhost:9092
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the service**
   ```bash
   python app.py
   ```

## 📋 Features

### Food Recognition
- **Photo Upload**: Accept food images from users
- **AI Analysis**: Identify food items using computer vision
- **Nutrition Lookup**: Retrieve nutritional information
- **Portion Estimation**: Estimate serving sizes from images
- **Multi-food Detection**: Identify multiple items in single photo

### Nutritional Tracking
- **Calorie Counting**: Track daily caloric intake
- **Macronutrient Analysis**: Monitor protein, carbs, and fats
- **Micronutrient Tracking**: Vitamins and minerals
- **Meal Categorization**: Breakfast, lunch, dinner, snacks
- **Custom Portions**: Manual portion adjustments

### Data Analytics
- **Daily Summaries**: Daily nutrition breakdowns
- **Historical Trends**: Long-term eating patterns
- **Goal Tracking**: Progress toward nutrition goals
- **Comparative Analysis**: Period-over-period comparisons
- **Health Insights**: Personalized health recommendations

### Recommendations
- **Meal Suggestions**: AI-powered meal recommendations
- **Nutritional Balance**: Suggestions for balanced nutrition
- **Dietary Preferences**: Customized for user preferences
- **Seasonal Recommendations**: Seasonal food suggestions
- **Health-based Suggestions**: Recommendations based on health goals

## 🔄 API Endpoints

### Food Operations
- **POST** `/food/analyze` - Analyze food photo
- **GET** `/food/history` - Get food history
- **POST** `/food/log` - Manually log food
- **PUT** `/food/{id}` - Update food entry
- **DELETE** `/food/{id}` - Delete food entry

### Nutritional Data
- **GET** `/nutrition/today` - Today's nutrition summary
- **GET** `/nutrition/date/{date}` - Specific date nutrition
- **GET** `/nutrition/trends` - Nutrition trends
- **GET** `/nutrition/goals` - User nutrition goals
- **POST** `/nutrition/goals` - Set nutrition goals

### Recommendations
- **GET** `/recommendations/meals` - Get meal recommendations
- **GET** `/recommendations/nutrition` - Get nutrition recommendations
- **POST** `/recommendations/feedback` - Provide feedback on recommendations

### Weight Tracking
- **POST** `/weight/log` - Log weight entry
- **GET** `/weight/history` - Weight history
- **GET** `/weight/trends` - Weight trends

## 🗄️ Database Schema

### Food Entries
```sql
CREATE TABLE food_entries (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    food_name VARCHAR(255) NOT NULL,
    calories INTEGER,
    protein DECIMAL(5,2),
    carbs DECIMAL(5,2),
    fats DECIMAL(5,2),
    portion_size VARCHAR(100),
    meal_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_url VARCHAR(500),
    analysis_confidence DECIMAL(3,2)
);
```

### Weight Entries
```sql
CREATE TABLE weight_entries (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

### Nutrition Goals
```sql
CREATE TABLE nutrition_goals (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    daily_calories INTEGER,
    protein_target DECIMAL(5,2),
    carbs_target DECIMAL(5,2),
    fats_target DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 AI Integration

### Photo Analysis Flow
1. **Image Upload**: User uploads food photo
2. **Pre-processing**: Image optimization and validation
3. **Vision Service**: Send to computer vision service
4. **Food Recognition**: AI identifies food items
5. **Nutrition Lookup**: Retrieve nutritional data
6. **Confidence Scoring**: Assign confidence levels
7. **User Confirmation**: Present results for user verification

### Recommendation Algorithm
```python
def generate_recommendations(user_profile, nutrition_history):
    # Analyze user preferences
    # Consider nutritional gaps
    # Factor in dietary restrictions
    # Generate personalized suggestions
    # Rank recommendations by relevance
    return recommended_meals
```

## 📊 Analytics & Insights

### Daily Metrics
- Total calories consumed
- Macronutrient breakdown
- Meal timing patterns
- Hydration tracking
- Goal achievement status

### Weekly/Monthly Trends
- Weight progression
- Nutrition consistency
- Meal diversity
- Goal adherence
- Health score trends

### Personalized Insights
- Nutrition recommendations
- Meal timing suggestions
- Portion size guidance
- Balance recommendations
- Health goal progress

## 🔐 Security & Privacy

### Data Protection
- Encrypted data storage
- Secure image handling
- User data anonymization
- GDPR compliance
- Data retention policies

### API Security
- Authentication required for all endpoints
- Rate limiting on image uploads
- Input validation and sanitization
- Secure file upload handling
- Audit logging

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eater-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: eater-service
  template:
    spec:
      containers:
      - name: eater-service
        image: your-registry/eater-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: POSTGRES_HOST
          value: "postgres-service"
        - name: BOOTSTRAP_SERVER
          value: "kafka-service:9092"
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
```

## 📊 Monitoring

### Health Checks
- Database connectivity
- Kafka broker status
- Vision service availability
- File system storage
- Memory usage

### Performance Metrics
- Image processing times
- Database query performance
- Recommendation generation speed
- API response times
- Error rates

### Business Metrics
- Daily active users
- Food entries per user
- Recommendation acceptance rates
- Goal achievement rates
- User retention metrics

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=eater/
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/

# Test with real services
pytest tests/integration/ --live-services
```

### Performance Testing
```bash
# Load testing
locust -f tests/load/locustfile.py

# Database performance
pytest tests/performance/database_tests.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow coding standards
- Add comprehensive logging
- Include unit tests for new features
- Update documentation as needed
- Consider performance implications

 