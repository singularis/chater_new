# Chater DLP Service

Google Cloud Data Loss Prevention (DLP) integration service providing advanced sensitive data detection, classification, and protection for the Chater platform.

## 🎯 Purpose

The Chater DLP Service provides comprehensive data protection functionality, including:
- Sensitive data detection and classification
- Personally Identifiable Information (PII) protection
- Content filtering and sanitization
- Privacy compliance and governance
- Real-time data scanning and analysis
- Automated redaction and de-identification

## 🏗️ Architecture

### Core Components
- **DLP Client**: Google Cloud DLP API integration
- **Content Scanner**: Real-time content analysis and scanning
- **Classification Engine**: Data classification and sensitivity scoring
- **Redaction Service**: Automatic data redaction and masking
- **Policy Engine**: Configurable privacy policies and rules
- **Audit Logger**: Comprehensive privacy and compliance logging

### Dependencies
- **Google Cloud DLP API**: Primary data loss prevention service
- **Apache Kafka**: Message broker for content scanning requests
- **Google Cloud Storage**: Optional secure temporary storage
- **Logging Framework**: Compliance and audit logging

## 🔧 Configuration

### Environment Variables
```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id
DLP_LOCATION=global

# Kafka Configuration
BOOTSTRAP_SERVER=your-kafka-broker:port
CONSUMER_GROUP=chater-dlp-group

# DLP Configuration
DETECTION_CONFIDENCE=POSSIBLE
INSPECTION_TEMPLATE=projects/your-project/inspectTemplates/default
DEIDENTIFY_TEMPLATE=projects/your-project/deidentifyTemplates/default

# Service Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
BATCH_SIZE=10

# Privacy Configuration
REDACTION_TYPE=MASK
MASK_CHARACTER=*
PRESERVE_FORMAT=true
```

### Kafka Topics
- **Consumes**: `content-scan`, `message-filter` - Content scanning requests
- **Produces**: `scan-results`, `filtered-content` - DLP analysis results

## 🚀 Getting Started

### Prerequisites
- Google Cloud Project with DLP API enabled
- Service account with DLP permissions
- Apache Kafka broker
- Python 3.8+ or Docker environment

### Installation
1. **Install dependencies**
   ```bash
   pip install google-cloud-dlp confluent-kafka python-dotenv
   ```

2. **Configure Google Cloud credentials**
   ```bash
   # Set service account key
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
   
   # Set project ID
   export GCP_PROJECT_ID=your-project-id
   ```

3. **Configure DLP templates**
   ```bash
   # Create inspection template
   gcloud dlp inspect-templates create \
     --location=global \
     --inspect-template-file=templates/inspect-template.json
   
   # Create de-identification template
   gcloud dlp deidentify-templates create \
     --location=global \
     --deidentify-template-file=templates/deidentify-template.json
   ```

4. **Run the service**
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

### Sensitive Data Detection
- **PII Detection**: Social Security Numbers, credit cards, phone numbers
- **Financial Data**: Bank accounts, routing numbers, financial IDs
- **Healthcare Data**: Medical record numbers, health insurance IDs
- **Personal Information**: Email addresses, names, addresses
- **Custom Patterns**: User-defined sensitive data patterns
- **Context Analysis**: Contextual sensitivity analysis

### Data Classification
- **Sensitivity Scoring**: Automatic sensitivity level assignment
- **Data Categories**: Classification by data type and domain
- **Risk Assessment**: Privacy risk evaluation
- **Compliance Mapping**: Map to regulatory requirements
- **Custom Taxonomies**: Organization-specific classifications
- **Multi-language Support**: Support for multiple languages

### Protection Mechanisms
- **Redaction**: Remove or mask sensitive information
- **Tokenization**: Replace sensitive data with tokens
- **Encryption**: Encrypt sensitive data in place
- **Hashing**: One-way hashing of sensitive values
- **Bucketing**: Group similar values into ranges
- **Date Shifting**: Shift dates while preserving relationships

### Privacy Compliance
- **GDPR Compliance**: European privacy regulation compliance
- **CCPA Compliance**: California privacy law compliance
- **HIPAA Compliance**: Healthcare privacy requirements
- **PCI DSS**: Payment card industry standards
- **Custom Policies**: Organization-specific privacy policies
- **Audit Trails**: Comprehensive compliance logging

## 🔄 Message Processing

### Request Format
```json
{
  "key": "unique-request-id",
  "value": {
    "content": "Text content to scan for sensitive data",
    "content_type": "text/plain",
    "user_email": "user@example.com",
    "scan_config": {
      "info_types": [
        "PERSON_NAME",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD_NUMBER"
      ],
      "min_likelihood": "POSSIBLE",
      "include_quote": true,
      "max_findings": 100
    },
    "action": "scan_and_redact",
    "preserve_format": true
  }
}
```

### Response Format
```json
{
  "key": "unique-request-id",
  "value": {
    "scan_results": {
      "findings": [
        {
          "info_type": "PERSON_NAME",
          "likelihood": "VERY_LIKELY",
          "location": {
            "byte_range": {
              "start": 10,
              "end": 20
            }
          },
          "quote": "John Smith",
          "finding_id": "finding-123"
        }
      ],
      "total_findings": 5,
      "risk_score": 0.8
    },
    "protected_content": "Hello [PERSON_NAME], your order...",
    "redactions_made": 3,
    "processing_time": 1.2,
    "timestamp": "2024-01-01T00:00:00Z",
    "compliance_status": "COMPLIANT"
  }
}
```

### Processing Flow
1. **Message Consumption**: Receive content scanning requests
2. **Content Validation**: Validate content format and size
3. **DLP Inspection**: Scan content using Google Cloud DLP
4. **Classification**: Classify and score findings
5. **Protection Application**: Apply redaction or masking
6. **Compliance Check**: Verify compliance requirements
7. **Audit Logging**: Log all privacy actions
8. **Response Generation**: Send results to Kafka

## 🛡️ Data Protection

### Detection Capabilities
```python
class DLPScanner:
    def __init__(self):
        self.dlp_client = dlp.DlpServiceClient()
        self.project_id = os.getenv('GCP_PROJECT_ID')
    
    def scan_content(self, content, info_types):
        # Configure inspection
        inspect_config = {
            "info_types": [{"name": info_type} for info_type in info_types],
            "min_likelihood": dlp.Likelihood.POSSIBLE,
            "include_quote": True,
        }
        
        # Perform inspection
        response = self.dlp_client.inspect_content(
            request={
                "parent": f"projects/{self.project_id}",
                "inspect_config": inspect_config,
                "item": {"value": content},
            }
        )
        
        return self.process_findings(response.result.findings)
```

### Protection Strategies
- **Masking**: Replace characters with mask symbols
- **Tokenization**: Replace with reversible tokens
- **Redaction**: Complete removal of sensitive data
- **Bucketing**: Replace with value ranges
- **Date Shifting**: Shift dates randomly within range
- **Crypto Hashing**: One-way hashing with salt

### Custom Info Types
```json
{
  "name": "EMPLOYEE_ID",
  "regex": {
    "pattern": "EMP-[0-9]{6}"
  },
  "likelihood": "VERY_LIKELY"
}
```

## 📊 Monitoring & Compliance

### Privacy Metrics
- **Detection Accuracy**: Sensitive data detection rates
- **False Positives**: Incorrect detections
- **Coverage**: Content scanning coverage
- **Response Time**: Scanning and processing time
- **Compliance Score**: Overall compliance rating

### Audit Capabilities
- **Data Access Logs**: Track all data access
- **Processing Logs**: Record all DLP operations
- **Compliance Reports**: Generate compliance reports
- **Risk Assessments**: Privacy risk evaluations
- **Retention Tracking**: Data retention compliance

### Health Monitoring
```python
def health_check():
    checks = {
        "dlp_api": check_dlp_connection(),
        "kafka_broker": check_kafka_connection(),
        "templates": validate_dlp_templates(),
        "quota": check_api_quota(),
        "processing_queue": check_queue_depth()
    }
    return all(checks.values())
```

## 🔒 Security & Privacy

### Service Security
- **API Authentication**: Secure service account authentication
- **Network Security**: VPC and firewall configurations
- **Access Control**: Role-based access control (RBAC)
- **Encryption**: End-to-end encryption of sensitive data
- **Audit Logging**: Comprehensive security audit logs

### Privacy by Design
- **Data Minimization**: Process only necessary data
- **Purpose Limitation**: Use data only for stated purposes
- **Storage Limitation**: Minimize data retention periods
- **Accuracy**: Ensure data accuracy and quality
- **Transparency**: Clear privacy policies and procedures

### Compliance Framework
- **Policy Management**: Centralized privacy policy management
- **Risk Assessment**: Automated privacy risk assessments
- **Incident Response**: Privacy incident response procedures
- **Training**: Privacy awareness and training programs
- **Monitoring**: Continuous compliance monitoring

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY service-account.json /app/credentials/
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json
CMD ["python", "main.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chater-dlp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chater-dlp
  template:
    spec:
      containers:
      - name: chater-dlp
        image: your-registry/chater-dlp:latest
        env:
        - name: GCP_PROJECT_ID
          value: "your-project-id"
        - name: BOOTSTRAP_SERVER
          value: "kafka-service:9092"
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/var/secrets/google/service-account.json"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: gcp-credentials
          mountPath: /var/secrets/google
          readOnly: true
      volumes:
      - name: gcp-credentials
        secret:
          secretName: gcp-dlp-service-account
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Run with coverage
python -m pytest tests/unit/ --cov=chater_dlp/
```

### Integration Tests
```bash
# Test DLP API integration
python -m pytest tests/integration/test_dlp.py

# Test privacy compliance
python -m pytest tests/integration/test_compliance.py
```

### Privacy Testing
```bash
# Test sensitive data detection
python tests/privacy/detection_test.py

# Test redaction accuracy
python tests/privacy/redaction_test.py

# Test compliance scenarios
python tests/privacy/compliance_test.py
```

### Performance Testing
```bash
# Load test with multiple requests
python tests/load/load_test.py --concurrent=3 --requests=200

# Batch processing performance
python tests/performance/batch_test.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow Python coding standards (PEP 8)
- Implement comprehensive privacy controls
- Add extensive unit tests for privacy features
- Document all privacy-related changes
- Consider regulatory compliance requirements
- Monitor API usage and costs
- Ensure secure handling of sensitive data 