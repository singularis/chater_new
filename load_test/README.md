# Load Test Service

Performance and load testing service for the Chater platform using Locust to simulate user behavior and stress test the system.

## 🎯 Purpose

The Load Test Service provides comprehensive load testing functionality, including:
- Realistic user behavior simulation
- Performance benchmarking and stress testing
- API endpoint load testing with Protocol Buffers
- Concurrent user simulation
- Performance metrics and reporting
- Bottleneck identification
- Capacity planning data collection

## 🏗️ Architecture

### Core Components
- **Locust Framework**: Distributed load testing framework
- **ChaterUser Class**: Simulated user behavior patterns
- **Protocol Buffers**: Native protobuf message testing
- **Task Definitions**: Weighted task execution
- **Bearer Auth**: JWT token authentication support
- **Metrics Collector**: Real-time performance metrics

### Dependencies
- **Locust**: Load testing framework
- **Protocol Buffers**: Message serialization
- **Python Libraries**: requests, protobuf
- **JWT**: Authentication token support

## 🔧 Configuration

### Environment Variables
```bash
# Target Configuration
TARGET_HOST=http://chater-ui.chater-ui.svc.cluster.local:5000
EATER_TARGET_HOST=http://chater-ui.chater-ui.svc.cluster.local:5000

# Authentication
TEST_USER_TOKEN=your-jwt-token-here
TEST_USER_EMAIL=test@example.com

# Test Data
TEST_PHOTO_PATH=/path/to/test/image.png
TEST_PHOTO_TYPE=default_prompt
TEST_CUSTOM_DATE=15-01-2024
TEST_LANGUAGE_CODE=en

# Locust Configuration
LOCUST_USERS=10
LOCUST_SPAWN_RATE=2
LOCUST_RUN_TIME=5m
LOCUST_HOST=http://chater-ui.chater-ui.svc.cluster.local:5000

# Test Scenarios
TEST_RECOMMENDATION_DAYS=1
TEST_ALCOHOL_START=01-01-2024
TEST_ALCOHOL_END=07-01-2024
TEST_FEEDBACK_TEXT=Load test feedback message

# Authentication Test Data
TEST_AUTH_PROVIDER=google
TEST_AUTH_TOKEN=test-token
TEST_AUTH_EMAIL=loadtest@example.com
TEST_AUTH_NAME=Locust Tester
TEST_AUTH_PROFILE_URL=https://example.com/avatar.png
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ environment
- Access to Chater platform (staging/production)
- Valid JWT authentication token
- Test image file for photo upload tests
- Protocol Buffer definitions

### Installation
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Protocol Buffers**
   ```bash
   # If proto files are updated
   cd proto
   protoc --python_out=. *.proto
   ```

3. **Configure environment**
   ```bash
   # Set target host
   export TARGET_HOST=http://localhost:5000
   
   # Set authentication token
   export TEST_USER_TOKEN=your-jwt-token
   export TEST_USER_EMAIL=test@example.com
   
   # Set test photo path
   export TEST_PHOTO_PATH=./image.png
   ```

### Running Tests

#### Web UI Mode
```bash
# Start Locust web interface
locust -f locustfile.py --host http://localhost:5000

# Open browser to http://localhost:8089
# Configure users and spawn rate in UI
```

#### Headless Mode
```bash
# Run with specified parameters
locust -f locustfile.py \
  --host http://localhost:5000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless

# With specific tags
locust -f locustfile.py \
  --host http://localhost:5000 \
  --users 10 \
  --spawn-rate 2 \
  --tags full_flow \
  --headless

# Exclude specific tags
locust -f locustfile.py \
  --host http://localhost:5000 \
  --users 10 \
  --spawn-rate 2 \
  --exclude-tags auth \
  --headless
```

#### Distributed Mode
```bash
# Start master node
locust -f locustfile.py \
  --master \
  --expect-workers 3

# Start worker nodes (on different machines/containers)
locust -f locustfile.py --worker --master-host=master-ip
locust -f locustfile.py --worker --master-host=master-ip
locust -f locustfile.py --worker --master-host=master-ip
```

## 📋 Test Scenarios

### Full Flow Test (@tag: full_flow)
Simulates complete user journey through the platform:
1. **Photo Upload**: Send food photo for analysis
2. **Modify Record**: Double portion size (200%)
3. **Weight Entry**: Log manual weight entry
4. **Get Recommendations**: Request meal recommendations
5. **Fetch Today's Data**: Retrieve updated food records
6. **Delete Record**: Clean up test data

```python
@tag("full_flow")
@task(1)
def full_flow(self):
    # Complete user journey simulation
```

### Custom Date Query (@tag: custom_date)
Test historical data retrieval:
```python
@tag("custom_date")
@task(1)
def custom_date_query(self):
    # Query food data for specific date
```

### Language Setting (@tag: language)
Test user preference management:
```python
@tag("language")
@task(1)
def set_language(self):
    # Update user language preference
```

### Alcohol Tracking (@tag: alcohol)
Test alcohol consumption endpoints:
```python
@tag("alcohol")
@task(1)
def alcohol_latest(self):
    # Get today's alcohol summary

@tag("alcohol")
@task(1)
def alcohol_range(self):
    # Get alcohol data for date range
```

### Feedback Submission (@tag: feedback)
Test feedback system:
```python
@tag("feedback")
@task(1)
def submit_feedback(self):
    # Submit user feedback
```

### Authentication (@tag: auth)
Test authentication flow:
```python
@tag("auth")
@task(1)
def eater_auth(self):
    # Test OAuth authentication
```

## 🔄 Protocol Buffer Messages

### Photo Upload
```protobuf
message PhotoMessage {
    string time = 1;
    bytes photo_data = 2;
    string photoType = 3;
}
```

### Modify Food Record
```protobuf
message ModifyFoodRecordRequest {
    int64 time = 1;
    string user_email = 2;
    int32 percentage = 3;
}
```

### Manual Weight
```protobuf
message ManualWeightRequest {
    string user_email = 1;
    float weight = 2;
}
```

### Delete Food
```protobuf
message DeleteFoodRequest {
    int64 time = 1;
}
```

### Set Language
```protobuf
message SetLanguageRequest {
    string user_email = 1;
    string language_code = 2;
}
```

### Alcohol Range
```protobuf
message GetAlcoholRangeRequest {
    string start_date = 1;
    string end_date = 2;
}
```

## 📊 Metrics & Reporting

### Built-in Metrics
Locust automatically tracks:
- **Request Count**: Total requests per endpoint
- **Failure Rate**: Percentage of failed requests
- **Response Time**: Min, max, average, median, 95th percentile
- **Requests per Second**: Throughput metrics
- **Response Size**: Average response size per endpoint
- **Concurrent Users**: Active user simulation

### Custom Metrics
```python
# Add custom metrics in tasks
with self.client.get("/endpoint", catch_response=True) as response:
    if response.elapsed.total_seconds() > 2.0:
        response.failure("Response time exceeded 2 seconds")
```

### Export Reports
```bash
# Generate CSV reports
locust -f locustfile.py \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --csv=results/load_test \
  --html=results/report.html

# Output files:
# - results/load_test_stats.csv
# - results/load_test_stats_history.csv
# - results/load_test_failures.csv
# - results/report.html
```

## 🐳 Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY locustfile.py .
COPY proto/ ./proto/
COPY image.png .

# Run in headless mode by default
CMD ["locust", "-f", "locustfile.py", "--headless"]
```

### Kubernetes Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: load-test
spec:
  template:
    spec:
      containers:
      - name: locust
        image: your-registry/load-test:latest
        env:
        - name: TARGET_HOST
          value: "http://chater-ui.chater-ui.svc.cluster.local:5000"
        - name: TEST_USER_TOKEN
          valueFrom:
            secretKeyRef:
              name: load-test-secrets
              key: jwt-token
        - name: TEST_USER_EMAIL
          value: "loadtest@example.com"
        args:
          - "--host"
          - "http://chater-ui.chater-ui.svc.cluster.local:5000"
          - "--users"
          - "50"
          - "--spawn-rate"
          - "5"
          - "--run-time"
          - "5m"
          - "--headless"
      restartPolicy: Never
  backoffLimit: 3
```

### Kubernetes Deployment (Master/Worker)
```yaml
# Master deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: locust-master
  template:
    spec:
      containers:
      - name: locust
        image: your-registry/load-test:latest
        args: ["--master"]
        ports:
        - containerPort: 8089  # Web UI
        - containerPort: 5557  # Worker communication
---
# Worker deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: locust-worker
  template:
    spec:
      containers:
      - name: locust
        image: your-registry/load-test:latest
        args:
          - "--worker"
          - "--master-host=locust-master"
        env:
        - name: TARGET_HOST
          value: "http://chater-ui:5000"
        - name: TEST_USER_TOKEN
          valueFrom:
            secretKeyRef:
              name: load-test-secrets
              key: jwt-token
```

## 🧪 Test Strategies

### Smoke Test
Quick validation of basic functionality:
```bash
locust -f locustfile.py \
  --users 1 \
  --spawn-rate 1 \
  --run-time 1m \
  --headless
```

### Load Test
Test system under normal load:
```bash
locust -f locustfile.py \
  --users 50 \
  --spawn-rate 5 \
  --run-time 10m \
  --headless
```

### Stress Test
Find system breaking point:
```bash
locust -f locustfile.py \
  --users 200 \
  --spawn-rate 10 \
  --run-time 15m \
  --headless
```

### Spike Test
Test rapid load increase:
```bash
# Start with 10 users
locust -f locustfile.py \
  --users 10 \
  --spawn-rate 10 \
  --run-time 2m \
  --headless

# Then spike to 100 users
locust -f locustfile.py \
  --users 100 \
  --spawn-rate 50 \
  --run-time 5m \
  --headless
```

### Endurance Test
Long-running stability test:
```bash
locust -f locustfile.py \
  --users 30 \
  --spawn-rate 3 \
  --run-time 2h \
  --headless
```

### Scenario-Specific Tests
```bash
# Test only photo upload flow
locust -f locustfile.py \
  --tags full_flow \
  --users 20 \
  --spawn-rate 2 \
  --run-time 5m \
  --headless

# Test only alcohol tracking
locust -f locustfile.py \
  --tags alcohol \
  --users 10 \
  --spawn-rate 2 \
  --run-time 3m \
  --headless

# Test everything except auth
locust -f locustfile.py \
  --exclude-tags auth \
  --users 30 \
  --spawn-rate 3 \
  --run-time 10m \
  --headless
```

## 📈 Performance Benchmarks

### Expected Performance
- **Photo Upload**: < 5s response time (95th percentile)
- **Food Record Modification**: < 1s response time
- **Weight Entry**: < 500ms response time
- **Get Today's Data**: < 2s response time
- **Recommendations**: < 3s response time
- **Delete Record**: < 1s response time

### Throughput Targets
- **Low Load**: 10-20 requests/second
- **Normal Load**: 50-100 requests/second
- **High Load**: 200+ requests/second

### Resource Usage
- **Memory**: Monitor for memory leaks during endurance tests
- **CPU**: Should stay below 80% under normal load
- **Database**: Connection pool should not exhaust
- **Kafka**: No significant consumer lag

## 🔍 Troubleshooting

### Common Issues

**Connection Refused**
```
ConnectionError: Failed to establish connection
```
**Solution**: 
- Verify target host is reachable
- Check network policies/firewall
- Ensure service is running
- Test with curl first

**Authentication Failures**
```
401 Unauthorized
```
**Solution**:
- Verify TEST_USER_TOKEN is valid
- Check token expiration
- Ensure correct email in TEST_USER_EMAIL
- Generate fresh token if needed

**Photo Upload Failures**
```
FileNotFoundError: image.png not found
```
**Solution**:
- Verify TEST_PHOTO_PATH is correct
- Use absolute path if relative path fails
- Ensure file exists in container/pod
- Check file permissions

**High Failure Rate**
```
> 5% failures
```
**Solution**:
- Reduce spawn rate
- Check server logs for errors
- Verify database connections
- Check Kafka consumer lag
- Monitor resource utilization

**Slow Response Times**
```
Response time > expected
```
**Solution**:
- Check database query performance
- Review application logs
- Monitor Kafka lag
- Check network latency
- Review resource limits

## 🔐 Security Considerations

### Test Data
- Use dedicated test accounts
- Don't use production user credentials
- Isolate test environment from production
- Clean up test data after completion

### Token Management
- Store tokens in secrets, not code
- Rotate test tokens regularly
- Use short-lived tokens for testing
- Monitor for token leaks

### Load Testing Ethics
- **Get Permission**: Always get approval before load testing
- **Use Test Environment**: Never load test production without explicit approval
- **Respect Limits**: Don't DoS the system
- **Off-Hours**: Run heavy tests during low-traffic periods
- **Communication**: Inform team before running tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new test scenarios
4. Update documentation
5. Test your changes
6. Submit a pull request

### Development Guidelines
- Use meaningful task names
- Add appropriate tags to tasks
- Document expected performance
- Include error handling in tasks
- Use Protocol Buffers for API testing
- Follow existing code patterns

## 📚 Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [Load Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Performance Testing Patterns](https://martinfowler.com/articles/practical-test-pyramid.html#ContractTests)
- [JWT Authentication](https://jwt.io/)

## 📖 Test Reports

### Interpreting Results

**Response Time Distribution**
- **50th percentile (median)**: Half of requests are faster
- **95th percentile**: 95% of requests are faster
- **99th percentile**: 99% of requests are faster

**Failure Analysis**
- **< 1% failures**: Acceptable
- **1-5% failures**: Investigate
- **> 5% failures**: Critical issue

**Requests per Second**
- **Increasing**: Good scaling
- **Plateauing**: Bottleneck identified
- **Decreasing**: System degrading under load

### Sample Report
```
Type     Name                          # reqs      # fails |    Avg     Min     Max  Median  |   req/s failures/s
--------|---------------------------|-------------|--------|-----------------------------|-----------------------
POST     /eater_receive_photo           1000     0(0.00%) |   3200    1500    8500    3100  |   16.67    0.00
POST     /modify_food_record             800     0(0.00%) |    450     200    1200     420  |   13.33    0.00
POST     /manual_weight                  800     0(0.00%) |    280     150     650     260  |   13.33    0.00
GET      /eater_get_today               1200     5(0.42%) |    850     400    2100     800  |   20.00    0.08
POST     /delete_food                    750     0(0.00%) |    520     250     950     480  |   12.50    0.00
--------|---------------------------|-------------|--------|-----------------------------|-----------------------
         Aggregated                     4550     5(0.11%) |   1260     150    8500    1100  |   75.83    0.08
```

## 🎯 Best Practices

1. **Start Small**: Begin with low user count
2. **Gradual Ramp-Up**: Increase load gradually
3. **Monitor System**: Watch metrics during tests
4. **Realistic Scenarios**: Simulate actual user behavior
5. **Clean Data**: Remove test data after completion
6. **Document Results**: Save reports for comparison
7. **Iterate**: Optimize and retest
8. **Communicate**: Share results with team

