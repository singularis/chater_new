# Chater Authentication Service

Java-based authentication service providing JWT token management and Google OAuth integration for the Chater platform.

## 🎯 Purpose

The Authentication Service handles secure user authentication and authorization, including:
- JWT token generation and validation
- Google OAuth 2.0 integration
- Session management and security
- User authentication flows
- Token lifecycle management

## 🏗️ Architecture

### Core Components
- **AuthService**: Main authentication logic and JWT handling
- **OAuth Integration**: Google OAuth 2.0 implementation
- **Token Management**: JWT creation, validation, and refresh
- **Kafka Integration**: Message-based authentication requests
- **Security Layer**: Encryption and secure token handling

### Dependencies
- **Apache Kafka**: Message broker for authentication requests
- **Google OAuth API**: External authentication provider
- **JWT Library**: Token generation and validation
- **Security Framework**: Encryption and hashing utilities

## 🔧 Configuration

### Environment Variables
```bash
# Authentication
EATER_SECRET_KEY=your-jwt-secret-key
BOOTSTRAP_SERVERS=your-kafka-broker:port

# Google OAuth (if used)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Service Configuration
SERVER_PORT=8080
LOG_LEVEL=INFO
```

### Kafka Topics
- **Consumes**: `auth_requires_token` - Authentication requests
- **Produces**: `add_auth_token` - Authentication responses with tokens

## 🚀 Getting Started

### Prerequisites
- Java 11+
- Apache Kafka broker
- Maven or Gradle for build management

### Installation
1. **Build the service**
   ```bash
   mvn clean compile
   ```

2. **Run the service**
   ```bash
   mvn exec:java -Dexec.mainClass="org.chater.AuthService"
   ```

### Development Setup
```bash
# Install dependencies
mvn install

# Run in development mode
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

## 📋 Features

### JWT Token Management
- **Token Generation**: Create secure JWT tokens with user claims
- **Token Validation**: Verify token integrity and expiration
- **Token Refresh**: Renew tokens before expiration
- **Secure Signing**: RSA/HMAC signing algorithms

### Authentication Methods
- **Google OAuth**: Social login integration
- **Username/Password**: Traditional credentials (if implemented)
- **Token-Based**: JWT bearer token authentication
- **Session Management**: Secure session handling

### Security Features
- **Password Hashing**: Secure password storage
- **Token Encryption**: Encrypted token payload
- **Rate Limiting**: Authentication attempt limiting
- **Audit Logging**: Security event tracking

## 🔄 Message Processing

### Authentication Request Flow
```java
@Component
public class AuthenticationProcessor {
    
    @KafkaListener(topics = "auth_requires_token")
    public void processAuthRequest(String message) {
        // Parse authentication request
        // Validate user credentials
        // Generate JWT token
        // Send response to add_auth_token topic
    }
}
```

### Message Format
**Request Message:**
```json
{
  "key": "unique-request-id",
  "value": {
    "user_email": "user@example.com",
    "user_name": "User Name",
    "profile_picture_url": "https://example.com/avatar.jpg",
    "oauth_token": "google-oauth-token"
  }
}
```

**Response Message:**
```json
{
  "key": "unique-request-id",
  "value": {
    "token": "jwt-token-here",
    "expiresIn": 86400,
    "userEmail": "user@example.com",
    "userName": "User Name",
    "profilePictureURL": "https://example.com/avatar.jpg"
  }
}
```

## 🔐 Security Implementation

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",
    "name": "User Name",
    "iat": 1234567890,
    "exp": 1234654290,
    "aud": "chater-platform"
  }
}
```

### Token Validation Process
1. **Signature Verification**: Validate token signature
2. **Expiration Check**: Ensure token hasn't expired
3. **Claims Validation**: Verify required claims
4. **Audience Check**: Confirm token audience
5. **Issuer Validation**: Verify token issuer

## 🐳 Deployment

### Docker
```dockerfile
FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/chater-auth.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chater-auth
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chater-auth
  template:
    spec:
      containers:
      - name: chater-auth
        image: your-registry/chater-auth:latest
        ports:
        - containerPort: 8080
        env:
        - name: EATER_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: chater-auth-secrets
              key: EATER_SECRET_KEY
        - name: BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
```

## 📊 Monitoring

### Health Checks
- **Service Health**: Application health status
- **Kafka Connectivity**: Message broker connection
- **Token Validation**: Authentication system health
- **Memory Usage**: JVM memory monitoring

### Metrics
- Authentication success/failure rates
- Token generation and validation times
- Message processing throughput
- Error rates and types

### Logging
- Authentication attempts and results
- Token generation and validation events
- Security incidents and alerts
- Performance metrics

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
# Run integration tests
mvn verify -P integration-tests
```

### Security Testing
- Token validation testing
- Authentication flow testing
- Security vulnerability scanning
- Performance testing under load

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow Java coding standards
- Use proper error handling
- Add comprehensive logging
- Include unit tests for new features
- Update documentation as needed

 