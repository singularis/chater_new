# Chater: Intelligent Chat & Food Tracking Platform

A comprehensive microservices-based application that combines AI-powered chat functionality with intelligent food tracking capabilities. Built with modern cloud-native architecture and featuring seamless integrations with multiple AI providers.

## 🚀 Features

### 💬 AI-Powered Chat
- **Multi-Provider AI Integration**: Support for OpenAI GPT and Google Gemini models
- **Vision Processing**: Advanced image analysis and recognition capabilities
- **Intelligent Responses**: Context-aware conversations with memory persistence
- **Real-time Communication**: Kafka-based messaging for instant responses

### 🍽️ Smart Food Tracking
- **Photo Analysis**: AI-powered food recognition from images
- **Nutritional Insights**: Automated calorie and nutrient tracking
- **Personalized Recommendations**: AI-driven meal suggestions
- **Data Visualization**: Comprehensive food intake analytics

### 🔐 Enterprise Security
- **Multi-Factor Authentication**: JWT tokens with Google OAuth integration
- **Data Loss Prevention**: Google Cloud DLP integration for sensitive data protection
- **Session Management**: Redis-based secure session handling
- **Role-Based Access Control**: Fine-grained permission management

### 📊 Modern Architecture
- **Microservices Design**: Scalable, maintainable service architecture
- **Cloud-Native**: Built for Kubernetes with custom operators
- **Real-time Processing**: Apache Kafka for asynchronous communication
- **High Availability**: Resilient design with health checks and monitoring

## 🏗️ Architecture Overview

The system is composed of multiple specialized microservices, each handling specific functionality:

### Core Services
- **chater_ui**: Main Flask web application providing the user interface
- **admin_service**: Administrative functionality and feedback processing
- **chater_auth**: Authentication and authorization service
- **eater**: Food tracking and nutritional analysis service

### AI & Processing Services
- **chater_gpt**: OpenAI GPT integration service
- **chater_gemini**: Google Gemini AI integration service
- **chater-vision**: Image processing and computer vision service
- **chater_dlp**: Data Loss Prevention service for sensitive data handling

### Infrastructure Services
- **chater-operators**: Kubernetes operators for service management
- **Kafka**: Message broker for inter-service communication
- **Redis**: Caching and session management
- **PostgreSQL**: Primary data storage

## 🛠️ Technology Stack

### Backend Technologies
- **Python**: Flask web framework, data processing services
- **Java**: High-performance services for authentication and vision processing
- **Protocol Buffers**: Efficient inter-service communication
- **Apache Kafka**: Event streaming and messaging
- **PostgreSQL**: Relational database for persistent storage
- **Redis**: In-memory caching and session store

### AI & ML Services
- **OpenAI GPT**: Advanced language model integration
- **Google Gemini**: Multi-modal AI capabilities
- **Google Cloud Vision**: Image analysis and recognition
- **Google Cloud DLP**: Data loss prevention and privacy protection

### Infrastructure & DevOps
- **Kubernetes**: Container orchestration
- **Custom Operators**: Automated service management
- **Ansible**: Infrastructure as Code
- **Docker**: Containerization
- **Google Cloud Platform**: Cloud services and APIs

### Frontend Technologies
- **HTML/CSS/JavaScript**: Modern web interface
- **Flask Templates**: Server-side rendering
- **Bootstrap**: Responsive design framework

## 🚀 Getting Started

### Prerequisites
- **Kubernetes Cluster**: v1.20+ with operator support
- **Docker**: For building and running containers
- **Python 3.8+**: For running development services
- **Java 11+**: For authentication and vision services
- **Apache Kafka**: Message broker setup
- **PostgreSQL**: Database server
- **Redis**: Cache server

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chater.git
   cd chater
   ```

2. **Configure environment variables**
   - Copy `vars.yaml.example` to `vars.yaml`
   - Set your API keys and configuration values
   - Configure database and messaging endpoints

3. **Deploy services**
   ```bash
   ./deploy_all.sh
   ```

### Development Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up development environment**
   ```bash
   cp .env.example .env
   # Edit .env with your development configuration
   ```

3. **Run individual services**
   ```bash
   # Start the main UI service
   cd chater_ui
   python app/app.py

   # Start the admin service
   cd admin_service
   python app.py
   ```

## 📋 Service Descriptions

### 🌐 chater_ui
**Main Web Application**
- Flask-based web interface
- User authentication and session management
- Real-time chat interface
- Food tracking dashboard
- Google OAuth integration
- Background Kafka consumer service

**Key Features:**
- Session-based authentication
- Rate limiting and security headers
- File upload handling
- Real-time messaging
- Responsive web design

### 🔧 admin_service
**Administrative Backend**
- Feedback processing and management
- Database administration
- System monitoring endpoints
- Background task processing

**Key Features:**
- Kafka-based feedback processing
- PostgreSQL data management
- Health check endpoints
- Async task handling

### 🔐 chater_auth
**Authentication Service**
- JWT token generation and validation
- Google OAuth integration
- User session management
- Security policy enforcement

**Key Features:**
- JWT token lifecycle management
- OAuth provider integration
- Session security
- User authentication flows

### 🍽️ eater
**Food Tracking Service**
- Photo-based food recognition
- Nutritional analysis
- Meal tracking and history
- Personalized recommendations

**Key Features:**
- AI-powered food identification
- Calorie and nutrition tracking
- Custom meal logging
- Data visualization

### 🤖 chater_gpt
**OpenAI Integration**
- GPT model integration
- Conversation context management
- Response generation
- Vision model support

**Key Features:**
- Multi-model support (GPT-4, GPT-3.5)
- Vision capabilities
- Context-aware responses
- Rate limiting

### 💎 chater_gemini
**Google Gemini Integration**
- Gemini model integration
- Multi-modal AI capabilities
- Advanced reasoning
- Image understanding

**Key Features:**
- Gemini Pro and Flash models
- Multi-modal processing
- Advanced AI capabilities
- Real-time responses

### 👁️ chater-vision
**Computer Vision Service**
- Image processing and analysis
- Visual content understanding
- Object detection
- Scene analysis

**Key Features:**
- Advanced image recognition
- Visual question answering
- Content moderation
- Scene understanding

### 🛡️ chater_dlp
**Data Loss Prevention**
- Sensitive data detection
- Content filtering
- Privacy protection
- Compliance monitoring

**Key Features:**
- PII detection and redaction
- Content classification
- Privacy compliance
- Data governance

## 🔧 Configuration

### Service Configuration
Each service can be configured through environment variables:

```yaml
# Database Configuration
POSTGRES_HOST: your-database-host
POSTGRES_DB: your-database-name
POSTGRES_USER: your-database-user
POSTGRES_PASSWORD: your-database-password

# Message Broker
BOOTSTRAP_SERVER: your-kafka-broker:port

# Caching
REDIS_ENDPOINT: your-redis-host

# AI Services
OPENAI_API_KEY: your-openai-api-key
GEMINI_API_KEY: your-gemini-api-key

# Authentication
JWT_SECRET_KEY: your-jwt-secret
GOOGLE_OAUTH_CLIENT_ID: your-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET: your-oauth-client-secret
```

### Kubernetes Deployment
Services are deployed using Ansible playbooks and Kubernetes manifests:

```bash
# Deploy all services
ansible-playbook chater.yaml

# Deploy individual services
ansible-playbook chater_ui/chater_ui.yaml
ansible-playbook admin_service/admin.yaml
```

## 🚀 Deployment

### Production Deployment
1. **Prepare your Kubernetes cluster**
2. **Configure secrets and configmaps**
3. **Deploy infrastructure services** (Kafka, Redis, PostgreSQL)
4. **Deploy application services** using the provided Ansible playbooks
5. **Configure ingress and load balancing**

### Development Deployment
1. **Set up local development environment**
2. **Configure local services** (database, message broker)
3. **Run services individually** for development and testing

## 📊 Monitoring & Logging

### Health Checks
All services include health check endpoints:
- `GET /health` - Service health status
- `GET /ready` - Readiness probe
- `GET /metrics` - Service metrics

### Logging
- Structured logging with configurable levels
- ELK stack integration ready
- Request/response logging
- Error tracking and alerting

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add documentation for new features
- Ensure all tests pass

## 🏗️ Architecture Diagrams

### System Architecture
```mermaid
graph TB
    subgraph "External Services"
        OpenAI[OpenAI API]
        Gemini[Google Gemini API]
        GCP[Google Cloud Platform]
        OAuth[Google OAuth]
    end
    
    subgraph "Infrastructure Layer"
        K8s[Kubernetes Cluster]
        Kafka[Apache Kafka]
        Redis[Redis Cache]
        PostgreSQL[PostgreSQL Database]
    end
    
    subgraph "Core Services"
        UI[chater_ui<br/>Flask Web App]
        Admin[admin_service<br/>Admin Backend]
        Auth[chater_auth<br/>Authentication]
        Eater[eater<br/>Food Tracking]
    end
    
    subgraph "AI Services"
        GPTService[chater_gpt<br/>OpenAI Integration]
        GeminiService[chater_gemini<br/>Gemini Integration]
        Vision[chater-vision<br/>Computer Vision]
        DLP[chater_dlp<br/>Data Loss Prevention]
    end
    
    subgraph "Management Layer"
        Operators[chater-operators<br/>K8s Operators]
    end
    
    %% User interactions
    User[User] --> UI
    UI --> OAuth
    
    %% Service interactions
    UI --> Kafka
    UI --> Redis
    UI --> Auth
    UI --> Eater
    
    Admin --> Kafka
    Admin --> PostgreSQL
    
    Auth --> Kafka
    Auth --> GCP
    
    Eater --> Kafka
    Eater --> PostgreSQL
    
    %% AI service interactions
    GPTService --> Kafka
    GPTService --> OpenAI
    
    GeminiService --> Kafka
    GeminiService --> Gemini
    
    Vision --> Kafka
    Vision --> Gemini
    
    DLP --> Kafka
    DLP --> GCP
    
    %% Kafka message flow
    Kafka --> GPTService
    Kafka --> GeminiService
    Kafka --> Vision
    Kafka --> DLP
    Kafka --> UI
    Kafka --> Admin
    Kafka --> Auth
    Kafka --> Eater
    
    %% Infrastructure management
    Operators --> K8s
    K8s --> UI
    K8s --> Admin
    K8s --> Auth
    K8s --> Eater
    K8s --> GPTService
    K8s --> GeminiService
    K8s --> Vision
    K8s --> DLP
    
    %% Data flow
    Redis --> UI
    PostgreSQL --> Admin
    PostgreSQL --> Eater
    
    %% External API connections
    GCP --> DLP
    GCP --> Vision
    GCP --> Auth
    OAuth --> UI
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef coreClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef aiClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef infraClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef externalClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef mgmtClass fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    
    class User userClass
    class UI,Admin,Auth,Eater coreClass
    class GPTService,GeminiService,Vision,DLP aiClass
    class K8s,Kafka,Redis,PostgreSQL infraClass
    class OpenAI,Gemini,GCP,OAuth externalClass
    class Operators mgmtClass
```

### Service Interaction Flow
```mermaid
sequenceDiagram
    participant User
    participant UI as chater_ui
    participant Kafka as Apache Kafka
    participant Auth as chater_auth
    participant GPT as chater_gpt
    participant Gemini as chater_gemini
    participant Vision as chater-vision
    participant DLP as chater_dlp
    participant Eater as eater
    participant Admin as admin_service
    participant Redis
    participant DB as PostgreSQL
    participant OpenAI as OpenAI API
    participant GeminiAPI as Gemini API
    
    Note over User,GeminiAPI: Chat Flow
    User->>UI: Submit chat message
    UI->>DLP: Check for sensitive data
    DLP-->>UI: Data validation response
    UI->>Kafka: Publish to gpt-send/gemini-send
    
    alt GPT Processing
        Kafka->>GPT: Consume message
        GPT->>OpenAI: Send request
        OpenAI-->>GPT: Return response
        GPT->>Kafka: Publish to gpt-response
    else Gemini Processing
        Kafka->>Gemini: Consume message
        Gemini->>GeminiAPI: Send request
        GeminiAPI-->>Gemini: Return response
        Gemini->>Kafka: Publish to gemini-response
    end
    
    Kafka->>UI: Consume response
    UI->>Redis: Cache response
    UI-->>User: Display response
    
    Note over User,GeminiAPI: Food Tracking Flow
    User->>UI: Upload food photo
    UI->>Kafka: Publish to chater-vision
    Kafka->>Vision: Consume message
    Vision->>GeminiAPI: Analyze image
    GeminiAPI-->>Vision: Return analysis
    Vision->>Kafka: Publish analysis result
    Kafka->>UI: Consume analysis
    UI->>Eater: Process food data
    Eater->>DB: Store food record
    UI-->>User: Display nutritional info
    
    Note over User,GeminiAPI: Authentication Flow
    User->>UI: Request authentication
    UI->>Kafka: Publish to auth_requires_token
    Kafka->>Auth: Consume auth request
    Auth->>Auth: Generate JWT token
    Auth->>Kafka: Publish to add_auth_token
    Kafka->>UI: Consume token response
    UI->>Redis: Store session
    UI-->>User: Authentication success
    
    Note over User,GeminiAPI: Feedback Flow
    User->>UI: Submit feedback
    UI->>Kafka: Publish to feedback
    Kafka->>Admin: Consume feedback
    Admin->>DB: Store feedback
    Admin-->>UI: Acknowledge receipt
    
    Note over User,GeminiAPI: Health Monitoring
    loop Health Checks
        UI->>Redis: Check connectivity
        UI->>Kafka: Check connectivity
        Admin->>DB: Check connectivity
        Auth->>Kafka: Check connectivity
    end
```

## 🙏 Acknowledgments

- OpenAI for GPT model integration
- Google Cloud Platform for AI and infrastructure services
- Apache Kafka for reliable messaging
- The open-source community for the foundational technologies



Built with ❤️ using modern cloud-native technologies 