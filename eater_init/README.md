# Eater Init Service

Database initialization and schema management service for the Chater platform, ensuring PostgreSQL database is properly configured with all required tables and indexes.

## 🎯 Purpose

The Eater Init Service provides database initialization functionality, including:
- Automated table creation and schema setup
- Database index creation for performance optimization
- Column validation and migration support
- Database health verification
- Query performance testing
- PostgreSQL extension management
- Multi-tenant schema support

## 🏗️ Architecture

### Core Components
- **Schema Manager**: SQLAlchemy ORM models for table definitions
- **Table Creator**: Automated table creation with retry logic
- **Index Builder**: Performance optimization through strategic indexing
- **Migration Handler**: Column addition and schema updates
- **Verification System**: Post-deployment validation
- **Performance Tester**: Query performance analysis

### Dependencies
- **SQLAlchemy**: ORM and database abstraction
- **PostgreSQL**: Primary database system
- **psycopg2**: PostgreSQL adapter for Python
- **Python Logging**: Comprehensive operation logging

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
POSTGRES_HOST=your-database-host
POSTGRES_DB=your-database-name
POSTGRES_USER=your-database-user
POSTGRES_PASSWORD=your-database-password
POSTGRES_PORT=5432

# Service Configuration
LOG_LEVEL=INFO
MAX_RETRIES=5
RETRY_DELAY=5

# Performance Settings
ENABLE_PERFORMANCE_TEST=true
VERIFY_INDEXES=true
```

## 🚀 Getting Started

### Prerequisites
- PostgreSQL 12+ server
- Database admin credentials
- Python 3.8+ environment
- Network access to PostgreSQL server

### Installation
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_DB=chater_db
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=your-password
   ```

3. **Run initialization**
   ```bash
   python create_tables.py
   ```

### Docker Deployment
```bash
# Build image
docker build -t eater-init:latest .

# Run as Kubernetes Job
kubectl apply -f eater_init_job.yaml
```

## 📋 Database Schema

### Tables Created

#### 1. User Table
```sql
CREATE TABLE public.user (
    email VARCHAR PRIMARY KEY,
    register_date VARCHAR,
    last_activity VARCHAR,
    language VARCHAR DEFAULT 'en'
);
```
**Purpose**: Store user profiles and preferences
**Indexes**:
- `idx_users_email_gin` - GIN index for fuzzy email search
- `idx_users_email` - B-tree index for exact lookups
- `idx_users_last_activity` - Track user engagement
- `idx_users_register_date` - Registration analytics

#### 2. Dishes Table
```sql
CREATE TABLE public.dishes (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    calories INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    ingredients ARRAY(VARCHAR) NOT NULL,
    contains JSON NOT NULL,
    user_email VARCHAR NOT NULL
);
```
**Purpose**: Master food database with nutritional information
**Indexes**:
- `idx_dishes_user_email` - User-specific dish lookups
- `idx_dishes_name` - Food name searches

#### 3. Dishes Day Table
```sql
CREATE TABLE public.dishes_day (
    time INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    dish_name VARCHAR NOT NULL,
    estimated_avg_calories INTEGER NOT NULL,
    ingredients ARRAY(VARCHAR) NOT NULL,
    total_avg_weight INTEGER NOT NULL,
    contains JSON NOT NULL,
    user_email VARCHAR NOT NULL
);
```
**Purpose**: Daily food consumption records
**Indexes**:
- `idx_dishes_day_user_email` - User filtering
- `idx_dishes_day_date` - Date-based queries
- `idx_dishes_day_time` - Timestamp lookups
- `idx_dishes_day_user_date` - Composite user+date queries
- `idx_dishes_day_user_time` - Composite user+time queries

#### 4. Total For Day Table
```sql
CREATE TABLE public.total_for_day (
    date DATE NOT NULL,
    user_email VARCHAR NOT NULL,
    total_calories INTEGER NOT NULL,
    ingredients ARRAY(VARCHAR) NOT NULL,
    dishes_of_day ARRAY(VARCHAR) NOT NULL,
    total_avg_weight INTEGER NOT NULL,
    contains JSON NOT NULL,
    today DATE NOT NULL,
    PRIMARY KEY (date, user_email)
);
```
**Purpose**: Daily nutritional summaries per user
**Indexes**:
- `idx_total_for_day_user_email` - User lookups
- `idx_total_for_day_today` - Current day queries
- `idx_total_for_day_user_today` - User daily summaries

#### 5. Weight Table
```sql
CREATE TABLE public.weight (
    time INTEGER PRIMARY KEY,
    date VARCHAR NOT NULL,
    weight FLOAT NOT NULL,
    user_email VARCHAR NOT NULL
);
```
**Purpose**: User weight tracking over time
**Indexes**:
- `idx_weight_user_email` - User weight history
- `idx_weight_time` - Timestamp queries
- `idx_weight_date` - Date-based lookups
- `idx_weight_user_time` - User+time composite

#### 6. Alcohol Consumption Table
```sql
CREATE TABLE public.alcohol_consumption (
    time INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    drink_name VARCHAR NOT NULL,
    calories INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    user_email VARCHAR NOT NULL
);
```
**Purpose**: Track alcohol consumption events
**Indexes**:
- `idx_alcohol_consumption_user_email` - User filtering
- `idx_alcohol_consumption_date` - Date queries
- `idx_alcohol_consumption_time` - Time lookups
- `idx_alcohol_consumption_user_time` - User+time composite

#### 7. Alcohol For Day Table
```sql
CREATE TABLE public.alcohol_for_day (
    date DATE NOT NULL,
    user_email VARCHAR NOT NULL,
    total_drinks INTEGER NOT NULL,
    total_calories INTEGER NOT NULL,
    drinks_of_day ARRAY(VARCHAR) NOT NULL,
    PRIMARY KEY (date, user_email)
);
```
**Purpose**: Daily alcohol consumption summaries
**Indexes**:
- `idx_alcohol_for_day_user_email` - User lookups
- `idx_alcohol_for_day_date` - Date queries
- `idx_alcohol_for_day_user_date` - User+date composite

## 🔧 Features

### Automated Schema Management
- **Table Creation**: Idempotent table creation with `CREATE IF NOT EXISTS`
- **Schema Versioning**: Track schema changes and updates
- **Rollback Safety**: Non-destructive operations, existing data preserved
- **Multi-Schema Support**: Public schema with namespace isolation

### Index Optimization
- **GIN Indexes**: Trigram search for fuzzy email matching
- **B-tree Indexes**: Fast exact match lookups
- **Composite Indexes**: Optimized multi-column queries
- **Partial Indexes**: Conditional indexing for performance
- **Performance Verification**: Post-creation query testing

### Migration Support
- **Column Addition**: Safe column addition with default values
- **Type Changes**: Handle data type migrations
- **Constraint Updates**: Add/modify constraints safely
- **Backward Compatibility**: Maintain compatibility with existing data

### Health Monitoring
- **Connection Testing**: Verify database connectivity
- **Table Verification**: Confirm all tables exist
- **Index Verification**: Validate index creation
- **Extension Check**: Verify PostgreSQL extensions
- **Query Performance**: Benchmark key queries

## 🔄 Initialization Flow

```
┌─────────────────────────┐
│  Start Initialization   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Load Environment Vars   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Connect to PostgreSQL   │
│  (with retry logic)      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Create Schema           │
│  (public)                │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Create Tables           │
│  (SQLAlchemy models)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Add Missing Columns     │
│  (migration support)     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Enable Extensions       │
│  (pg_trgm)               │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Create Indexes          │
│  (performance)           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Verify Indexes          │
│  (validation)            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Update Statistics       │
│  (ANALYZE)               │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Test Query Performance  │
│  (benchmarking)          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Initialization Complete │
└─────────────────────────┘
```

## 📊 Index Strategy

### Why These Indexes?

**Email Search Performance**
```sql
-- GIN index enables fast fuzzy search
CREATE INDEX idx_users_email_gin ON public.user 
USING gin(email gin_trgm_ops);

-- B-tree for exact matches
CREATE INDEX idx_users_email ON public.user 
USING btree(email);
```
**Use Case**: Autocomplete email search, user lookup

**User Food History**
```sql
-- Composite index for user's food on specific date
CREATE INDEX idx_dishes_day_user_date ON public.dishes_day 
USING btree(user_email, date);
```
**Use Case**: "Show me what I ate on January 15th"

**Time-based Queries**
```sql
-- Timestamp lookups for recent activity
CREATE INDEX idx_dishes_day_user_time ON public.dishes_day 
USING btree(user_email, time);
```
**Use Case**: "Get my latest food entry"

**Daily Summaries**
```sql
-- Fast daily nutrition totals
CREATE INDEX idx_total_for_day_user_today ON public.total_for_day 
USING btree(user_email, today);
```
**Use Case**: "Show today's total calories"

## 🐳 Deployment

### Kubernetes Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: eater-init
spec:
  template:
    spec:
      containers:
      - name: eater-init
        image: your-registry/eater-init:latest
        env:
        - name: POSTGRES_HOST
          value: "postgres-service"
        - name: POSTGRES_DB
          value: "chater_db"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
      restartPolicy: OnFailure
  backoffLimit: 3
```

### Helm Chart Integration
```yaml
# In your Helm values
eaterInit:
  enabled: true
  image:
    repository: your-registry/eater-init
    tag: latest
  postgresql:
    host: postgres-service
    database: chater_db
    existingSecret: postgres-credentials
```

### Init Container Pattern
```yaml
# Run as init container before main application
spec:
  initContainers:
  - name: db-init
    image: your-registry/eater-init:latest
    env:
    - name: POSTGRES_HOST
      value: "postgres-service"
    # ... other env vars
  containers:
  - name: main-app
    image: your-registry/chater-ui:latest
    # ... app config
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/unit/

# Test table creation
python -m pytest tests/unit/test_table_creation.py

# Test index creation
python -m pytest tests/unit/test_indexes.py
```

### Integration Tests
```bash
# Run integration tests (requires PostgreSQL)
python -m pytest tests/integration/

# Test full initialization flow
python -m pytest tests/integration/test_init_flow.py

# Test migration scenarios
python -m pytest tests/integration/test_migrations.py
```

### Manual Verification
```bash
# Check tables created
psql -h localhost -U postgres -d chater_db -c "\dt public.*"

# Check indexes
psql -h localhost -U postgres -d chater_db -c "\di public.*"

# Verify extensions
psql -h localhost -U postgres -d chater_db -c "\dx"

# Test query performance
psql -h localhost -U postgres -d chater_db -c "EXPLAIN ANALYZE SELECT * FROM public.user WHERE email LIKE '%test%';"
```

## 🔍 Troubleshooting

### Common Issues

**Connection Refused**
```
Error: could not connect to server
```
**Solution**: 
- Verify PostgreSQL is running
- Check host and port configuration
- Verify firewall rules
- Test with: `psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB`

**Permission Denied**
```
Error: permission denied for schema public
```
**Solution**:
```sql
-- Grant necessary permissions
GRANT ALL ON SCHEMA public TO your_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO your_user;
```

**Index Creation Timeout**
```
Error: timeout while creating index
```
**Solution**:
- Increase `RETRY_DELAY` and `MAX_RETRIES`
- Create indexes concurrently: `CREATE INDEX CONCURRENTLY`
- Check database load and available resources

**Table Already Exists**
```
Error: relation "user" already exists
```
**Solution**: This is normal! The script uses `CREATE IF NOT EXISTS` and will skip existing tables. Check logs to confirm.

**Missing Extension**
```
Error: extension "pg_trgm" does not exist
```
**Solution**:
```sql
-- Install extension (requires superuser)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Or install system-wide
sudo apt-get install postgresql-contrib
```

## 📚 Best Practices

### Before Running
1. **Backup Database**: Always backup before schema changes
2. **Test Environment**: Test in staging first
3. **Read-Only Check**: Verify application can handle initialization
4. **Monitoring**: Set up alerts for long-running operations

### After Running
1. **Verify Completion**: Check all tables and indexes created
2. **Test Performance**: Run benchmark queries
3. **Update Documentation**: Document any manual changes
4. **Monitor Logs**: Review initialization logs for warnings

### Maintenance
- **Regular ANALYZE**: Update table statistics periodically
- **Index Monitoring**: Watch for unused indexes
- **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
- **Vacuum**: Regular VACUUM to reclaim space

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for schema changes
5. Update documentation
6. Submit a pull request

### Development Guidelines
- Use SQLAlchemy ORM models for table definitions
- Add indexes judiciously (consider write performance)
- Document the purpose of each table and index
- Test migrations with existing data
- Include rollback procedures
- Log all operations clearly

## 📖 References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/14/core/)
- [pg_trgm Extension](https://www.postgresql.org/docs/current/pgtrgm.html)
- [PostgreSQL Indexing](https://www.postgresql.org/docs/current/indexes.html)
- [Database Migration Best Practices](https://www.postgresql.org/docs/current/sql-altertable.html)

