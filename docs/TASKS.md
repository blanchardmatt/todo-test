# Task List: Database Integration & User Management

**Project:** Todo Application - Phase 2 Enhancement
**Version:** 2.0
**Created:** December 2025
**Status:** Planning

---

## Table of Contents
1. [Overview](#overview)
2. [Goals & Objectives](#goals--objectives)
3. [Technical Decisions](#technical-decisions)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Task Breakdown](#detailed-task-breakdown)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Strategy](#deployment-strategy)
8. [Success Criteria](#success-criteria)

---

## Overview

This document outlines the tasks required to address two major limitations identified in the PRD:

1. **LIMIT-1: Data Persistence** - Replace in-memory storage with PostgreSQL database
2. **LIMIT-3: No User Authentication** - Implement user authentication and multi-tenancy

These enhancements will enable:
- Persistent data storage across pod restarts
- Horizontal scaling with multiple replicas
- Multi-user support with isolated todo lists
- Production-ready deployment architecture

---

## Goals & Objectives

### Primary Goals
- [ ] Implement PostgreSQL database for persistent storage
- [ ] Add user authentication system (OAuth 2.0)
- [ ] Enable multi-user support with data isolation
- [ ] Maintain backward compatibility with existing API
- [ ] Support horizontal scaling (multiple replicas)

### Secondary Goals
- [ ] Add database migration tooling
- [ ] Implement connection pooling
- [ ] Add caching layer (Redis) for performance
- [ ] Create admin dashboard for user management
- [ ] Implement audit logging

### Non-Goals (Out of Scope)
- Mobile application development
- Real-time collaboration features
- Task sharing between users
- Calendar integration
- Third-party integrations (Slack, etc.)

---

## Technical Decisions

### Database Selection: PostgreSQL

**Rationale:**
- Industry-standard relational database
- Native OpenShift support via templates
- Strong ACID compliance
- Excellent Python ecosystem (psycopg2, SQLAlchemy)
- Built-in JSON support for extensibility

**Alternatives Considered:**
- MongoDB: Rejected - overkill for simple data model
- MySQL: Rejected - less OpenShift integration
- SQLite: Rejected - not suitable for multi-pod deployments

### Authentication: OAuth 2.0 with Flask-Login

**Rationale:**
- Standards-based authentication
- Multiple provider support (Google, GitHub, Microsoft)
- Reduces password management burden
- Good user experience (SSO)

**Alternatives Considered:**
- JWT-only: Rejected - requires frontend changes
- Basic Auth: Rejected - poor security
- Custom auth: Rejected - reinventing the wheel

### ORM: SQLAlchemy

**Rationale:**
- De facto standard for Python ORMs
- Database-agnostic (easy to switch if needed)
- Migration support via Alembic
- Type safety and IDE support

### Session Management: Flask-Session + Redis

**Rationale:**
- Centralized session storage (multi-pod compatible)
- Fast in-memory lookups
- Automatic expiration
- OpenShift Redis template available

---

## Implementation Phases

### Phase 1: Database Foundation (Week 1-2)
**Goal:** Replace in-memory storage with PostgreSQL

- Set up PostgreSQL on OpenShift
- Design database schema
- Implement SQLAlchemy models
- Create migration scripts
- Update API to use database
- Maintain API compatibility

**Deliverables:**
- Working PostgreSQL deployment
- All todos persisted to database
- Zero API changes
- Migration from in-memory data

---

### Phase 2: User Authentication (Week 3-4)
**Goal:** Add user login and registration

- Implement OAuth 2.0 providers
- Add user model and sessions
- Create login/logout flows
- Add user registration
- Implement protected routes

**Deliverables:**
- Users can register/login
- Sessions persist across requests
- Protected API endpoints
- User profile page

---

### Phase 3: Multi-User Support (Week 5-6)
**Goal:** Isolate todos per user

- Add user_id foreign key to todos
- Filter todos by authenticated user
- Update UI for user context
- Add sharing capabilities (optional)

**Deliverables:**
- Each user sees only their todos
- User dashboard showing stats
- Admin panel for user management

---

### Phase 4: Production Hardening (Week 7-8)
**Goal:** Prepare for production deployment

- Implement connection pooling
- Add Redis caching layer
- Set up database backups
- Configure monitoring/alerting
- Load testing and optimization
- Security audit

**Deliverables:**
- Scalable to 10+ replicas
- < 100ms API response time
- 99.9% uptime SLA
- Security scan passing

---

## Detailed Task Breakdown

### Phase 1: Database Foundation

#### Task 1.1: PostgreSQL Setup
**Priority:** P0 (Blocker)
**Estimated Effort:** 4 hours
**Dependencies:** None

**Subtasks:**
- [ ] Deploy PostgreSQL on OpenShift using template
  ```bash
  oc new-app postgresql-persistent \
    -p POSTGRESQL_USER=todoapp \
    -p POSTGRESQL_PASSWORD=<secure-password> \
    -p POSTGRESQL_DATABASE=tododb
  ```
- [ ] Create database connection secret
- [ ] Add environment variables to deployment
- [ ] Test connectivity from application pod
- [ ] Document connection parameters in CLAUDE.md

**Acceptance Criteria:**
- PostgreSQL pod running and healthy
- Application can connect to database
- Connection credentials secured in OpenShift secret

---

#### Task 1.2: Database Schema Design
**Priority:** P0 (Blocker)
**Estimated Effort:** 2 hours
**Dependencies:** None

**Subtasks:**
- [ ] Design `users` table schema
  ```sql
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] Design `todos` table schema
  ```sql
  CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] Create indexes for performance
  ```sql
  CREATE INDEX idx_todos_user_id ON todos(user_id);
  CREATE INDEX idx_todos_completed ON todos(completed);
  CREATE INDEX idx_users_email ON users(email);
  ```

- [ ] Document schema in `docs/DATABASE.md`

**Acceptance Criteria:**
- Schema supports all current features
- Indexes created for query optimization
- Foreign key constraints enforced
- Schema documented

---

#### Task 1.3: Add Dependencies
**Priority:** P0 (Blocker)
**Estimated Effort:** 1 hour
**Dependencies:** None

**Subtasks:**
- [ ] Update `config/requirements.txt`:
  ```
  Flask==3.0.0
  Werkzeug==3.0.1
  gunicorn==21.2.0
  SQLAlchemy==2.0.23
  psycopg2-binary==2.9.9
  alembic==1.12.1
  Flask-SQLAlchemy==3.1.1
  Flask-Migrate==4.0.5
  ```
- [ ] Install and test locally
- [ ] Update Dockerfile with new dependencies
- [ ] Test container build

**Acceptance Criteria:**
- All dependencies install without errors
- No version conflicts
- Docker build succeeds

---

#### Task 1.4: Implement SQLAlchemy Models
**Priority:** P0 (Blocker)
**Estimated Effort:** 3 hours
**Dependencies:** Task 1.2, Task 1.3

**Subtasks:**
- [ ] Create `src/models.py`:
  ```python
  from flask_sqlalchemy import SQLAlchemy
  from datetime import datetime

  db = SQLAlchemy()

  class User(db.Model):
      __tablename__ = 'users'

      id = db.Column(db.Integer, primary_key=True)
      email = db.Column(db.String(255), unique=True, nullable=False)
      name = db.Column(db.String(255), nullable=False)
      oauth_provider = db.Column(db.String(50))
      oauth_id = db.Column(db.String(255))
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

      todos = db.relationship('Todo', backref='user', cascade='all, delete-orphan')

      def to_dict(self):
          return {
              'id': self.id,
              'email': self.email,
              'name': self.name,
              'created_at': self.created_at.isoformat()
          }

  class Todo(db.Model):
      __tablename__ = 'todos'

      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
      text = db.Column(db.Text, nullable=False)
      completed = db.Column(db.Boolean, default=False)
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

      def to_dict(self):
          return {
              'id': self.id,
              'text': self.text,
              'completed': self.completed
          }
  ```

- [ ] Add model unit tests
- [ ] Test model relationships

**Acceptance Criteria:**
- Models map correctly to database schema
- Relationships work bidirectionally
- `to_dict()` methods serialize correctly
- Unit tests pass

---

#### Task 1.5: Database Configuration
**Priority:** P0 (Blocker)
**Estimated Effort:** 2 hours
**Dependencies:** Task 1.1, Task 1.3

**Subtasks:**
- [ ] Create `src/config.py`:
  ```python
  import os

  class Config:
      # Database
      SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
          'postgresql://todoapp:password@localhost/tododb'
      SQLALCHEMY_TRACK_MODIFICATIONS = False
      SQLALCHEMY_ENGINE_OPTIONS = {
          'pool_size': 10,
          'pool_recycle': 3600,
          'pool_pre_ping': True
      }

      # Flask
      SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'

      # Session
      SESSION_TYPE = 'redis'
      SESSION_REDIS = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
  ```

- [ ] Update `src/app.py` to load config
- [ ] Add environment variable documentation
- [ ] Test with local PostgreSQL

**Acceptance Criteria:**
- Configuration loaded from environment
- Database connection successful
- Connection pooling configured
- Works with both local and OpenShift databases

---

#### Task 1.6: Migrate API to Use Database
**Priority:** P0 (Blocker)
**Estimated Effort:** 6 hours
**Dependencies:** Task 1.4, Task 1.5

**Subtasks:**
- [ ] Update `GET /api/todos`:
  ```python
  @app.route('/api/todos', methods=['GET'])
  def get_todos():
      # For now, use default user (user_id=1) until auth is implemented
      user_id = session.get('user_id', 1)
      todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.created_at.desc()).all()
      return jsonify([todo.to_dict() for todo in todos])
  ```

- [ ] Update `POST /api/todos`:
  ```python
  @app.route('/api/todos', methods=['POST'])
  def add_todo():
      data = request.get_json()
      if not data or 'text' not in data:
          return jsonify({'error': 'Todo text is required'}), 400

      user_id = session.get('user_id', 1)
      todo = Todo(user_id=user_id, text=data['text'])
      db.session.add(todo)
      db.session.commit()

      return jsonify(todo.to_dict()), 201
  ```

- [ ] Update `PUT /api/todos/<id>`:
  ```python
  @app.route('/api/todos/<int:todo_id>', methods=['PUT'])
  def update_todo(todo_id):
      user_id = session.get('user_id', 1)
      todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()

      if not todo:
          return jsonify({'error': 'Todo not found'}), 404

      data = request.get_json()
      if 'completed' in data:
          todo.completed = data['completed']
      if 'text' in data:
          todo.text = data['text']

      db.session.commit()
      return jsonify(todo.to_dict())
  ```

- [ ] Update `DELETE /api/todos/<id>`:
  ```python
  @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
  def delete_todo(todo_id):
      user_id = session.get('user_id', 1)
      todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()

      if not todo:
          return jsonify({'error': 'Todo not found'}), 404

      result = todo.to_dict()
      db.session.delete(todo)
      db.session.commit()

      return jsonify(result)
  ```

- [ ] Remove in-memory storage (`todos = []`, `todo_id_counter`)
- [ ] Test all endpoints
- [ ] Verify backward compatibility

**Acceptance Criteria:**
- All API endpoints work with database
- No breaking changes to API contract
- Error handling for database failures
- Existing Playwright tests pass

---

#### Task 1.7: Database Migrations
**Priority:** P1 (Important)
**Estimated Effort:** 3 hours
**Dependencies:** Task 1.4

**Subtasks:**
- [ ] Initialize Alembic:
  ```bash
  flask db init
  ```

- [ ] Create initial migration:
  ```bash
  flask db migrate -m "Initial schema with users and todos"
  ```

- [ ] Review generated migration script
- [ ] Test migration:
  ```bash
  flask db upgrade
  ```

- [ ] Test rollback:
  ```bash
  flask db downgrade
  ```

- [ ] Create seed data script (`scripts/seed_data.py`)
- [ ] Document migration workflow in CLAUDE.md

**Acceptance Criteria:**
- Migrations run successfully
- Rollback works correctly
- Seed data script populates test data
- Migration commands documented

---

#### Task 1.8: Update Deployment for Database
**Priority:** P0 (Blocker)
**Estimated Effort:** 3 hours
**Dependencies:** Task 1.5

**Subtasks:**
- [ ] Update `config/openshift-deployment.yaml`:
  ```yaml
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: postgresql-secret
          key: database-url
    - name: SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: secret-key
  ```

- [ ] Create database secret template
- [ ] Add init container for migrations:
  ```yaml
  initContainers:
    - name: db-migrate
      image: todo-app:latest
      command: ['flask', 'db', 'upgrade']
      env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: database-url
  ```

- [ ] Update health check to verify DB connection
- [ ] Test deployment on OpenShift

**Acceptance Criteria:**
- Application connects to PostgreSQL
- Migrations run automatically on deployment
- Secrets properly configured
- Health checks pass

---

### Phase 2: User Authentication

#### Task 2.1: Add Authentication Dependencies
**Priority:** P0 (Blocker)
**Estimated Effort:** 1 hour
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Update `config/requirements.txt`:
  ```
  Flask-Login==0.6.3
  authlib==1.2.1
  Flask-Dance==7.0.0
  python-dotenv==1.0.0
  ```
- [ ] Install and test locally
- [ ] Update Dockerfile

**Acceptance Criteria:**
- Dependencies install successfully
- No conflicts with existing packages

---

#### Task 2.2: Implement OAuth Providers
**Priority:** P0 (Blocker)
**Estimated Effort:** 8 hours
**Dependencies:** Task 2.1

**Subtasks:**
- [ ] Set up Google OAuth:
  - Register app at Google Cloud Console
  - Obtain client ID and secret
  - Configure redirect URIs

- [ ] Set up GitHub OAuth:
  - Register app at GitHub Developer Settings
  - Obtain client ID and secret
  - Configure callback URLs

- [ ] Create `src/auth.py`:
  ```python
  from flask import Blueprint, redirect, url_for, session
  from flask_login import LoginManager, login_user, logout_user, login_required
  from flask_dance.contrib.google import make_google_blueprint, google
  from flask_dance.contrib.github import make_github_blueprint, github
  from src.models import User, db

  auth_bp = Blueprint('auth', __name__)
  login_manager = LoginManager()

  google_bp = make_google_blueprint(
      client_id=os.environ.get('GOOGLE_CLIENT_ID'),
      client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
      scope=['profile', 'email']
  )

  github_bp = make_github_blueprint(
      client_id=os.environ.get('GITHUB_CLIENT_ID'),
      client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
      scope='user:email'
  )

  @auth_bp.route('/login/google')
  def login_google():
      if not google.authorized:
          return redirect(url_for('google.login'))

      resp = google.get('/oauth2/v2/userinfo')
      user_info = resp.json()

      user = User.query.filter_by(email=user_info['email']).first()
      if not user:
          user = User(
              email=user_info['email'],
              name=user_info['name'],
              oauth_provider='google',
              oauth_id=user_info['id']
          )
          db.session.add(user)
          db.session.commit()

      login_user(user)
      return redirect(url_for('index'))

  @auth_bp.route('/logout')
  @login_required
  def logout():
      logout_user()
      return redirect(url_for('index'))
  ```

- [ ] Register blueprints in `src/app.py`
- [ ] Test OAuth flow with both providers

**Acceptance Criteria:**
- Users can log in with Google
- Users can log in with GitHub
- User created on first login
- Session persists across requests

---

#### Task 2.3: Protect API Routes
**Priority:** P0 (Blocker)
**Estimated Effort:** 3 hours
**Dependencies:** Task 2.2

**Subtasks:**
- [ ] Add `@login_required` decorator to API routes
- [ ] Update routes to use `current_user.id` instead of hardcoded user_id
- [ ] Add proper 401 responses for unauthenticated requests
- [ ] Update frontend to handle authentication

**Example:**
```python
from flask_login import login_required, current_user

@app.route('/api/todos', methods=['GET'])
@login_required
def get_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify([todo.to_dict() for todo in todos])
```

**Acceptance Criteria:**
- Unauthenticated users cannot access API
- Authenticated users see only their todos
- Clear error messages for auth failures

---

#### Task 2.4: Update Frontend for Authentication
**Priority:** P0 (Blocker)
**Estimated Effort:** 6 hours
**Dependencies:** Task 2.3

**Subtasks:**
- [ ] Add login page to `templates/login.html`
- [ ] Add user profile dropdown to `templates/index.html`
- [ ] Show/hide UI based on auth state
- [ ] Add logout button
- [ ] Redirect to login if unauthenticated
- [ ] Display user name/avatar

**Acceptance Criteria:**
- Login page displays OAuth buttons
- Authenticated users see their profile
- Logout works correctly
- UI clearly shows auth state

---

#### Task 2.5: Redis Session Storage
**Priority:** P1 (Important)
**Estimated Effort:** 4 hours
**Dependencies:** Task 2.2

**Subtasks:**
- [ ] Deploy Redis on OpenShift:
  ```bash
  oc new-app redis-persistent --name=redis
  ```

- [ ] Add Flask-Session configuration
- [ ] Update deployment with Redis URL
- [ ] Test session persistence across pods
- [ ] Set session expiration (24 hours)

**Acceptance Criteria:**
- Sessions stored in Redis
- Sessions work with multiple replicas
- Sessions expire after 24 hours
- Redis deployment is persistent

---

### Phase 3: Multi-User Support

#### Task 3.1: User Dashboard
**Priority:** P2 (Nice to Have)
**Estimated Effort:** 4 hours
**Dependencies:** Phase 2 complete

**Subtasks:**
- [ ] Create `/dashboard` route
- [ ] Display user statistics:
  - Total todos
  - Completed todos
  - Completion rate
  - Recent activity
- [ ] Add charts (Chart.js or similar)

**Acceptance Criteria:**
- Dashboard shows meaningful stats
- Visualizations are clear
- Responsive on mobile

---

#### Task 3.2: User Settings
**Priority:** P2 (Nice to Have)
**Estimated Effort:** 3 hours
**Dependencies:** Phase 2 complete

**Subtasks:**
- [ ] Create `/settings` route
- [ ] Allow users to update:
  - Display name
  - Email preferences
  - Theme (dark mode)
- [ ] Add account deletion option

**Acceptance Criteria:**
- Users can update settings
- Changes persist to database
- Account deletion removes all data

---

#### Task 3.3: Admin Panel (Optional)
**Priority:** P3 (Low)
**Estimated Effort:** 8 hours
**Dependencies:** Phase 2 complete

**Subtasks:**
- [ ] Add `is_admin` flag to User model
- [ ] Create `/admin` route (admin-only)
- [ ] Display all users
- [ ] View user statistics
- [ ] Disable/enable user accounts

**Acceptance Criteria:**
- Only admins can access admin panel
- Admins can view all users
- Admins can manage user accounts

---

### Phase 4: Production Hardening

#### Task 4.1: Database Connection Pooling
**Priority:** P1 (Important)
**Estimated Effort:** 2 hours
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Configure SQLAlchemy pool parameters
- [ ] Add connection health checks
- [ ] Test under load
- [ ] Monitor connection usage

**Acceptance Criteria:**
- Pool size optimized for workload
- No connection leaks
- Handles database restarts gracefully

---

#### Task 4.2: Caching Layer
**Priority:** P2 (Nice to Have)
**Estimated Effort:** 6 hours
**Dependencies:** Task 2.5 (Redis deployed)

**Subtasks:**
- [ ] Add Flask-Caching:
  ```python
  from flask_caching import Cache
  cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': redis_url})
  ```

- [ ] Cache user queries
- [ ] Cache todo list for 30 seconds
- [ ] Invalidate cache on updates
- [ ] Add cache hit/miss metrics

**Acceptance Criteria:**
- Read operations use cache when possible
- Cache invalidation works correctly
- Performance improvement measurable

---

#### Task 4.3: Database Backups
**Priority:** P0 (Blocker)
**Estimated Effort:** 4 hours
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Configure PostgreSQL backups in OpenShift
- [ ] Set up CronJob for daily backups:
  ```yaml
  apiVersion: batch/v1
  kind: CronJob
  metadata:
    name: postgres-backup
  spec:
    schedule: "0 2 * * *"  # 2 AM daily
    jobTemplate:
      spec:
        template:
          spec:
            containers:
            - name: backup
              image: postgres:13
              command: ['/bin/bash', '-c', 'pg_dump -h postgresql -U todoapp tododb | gzip > /backups/backup-$(date +%Y%m%d).sql.gz']
  ```

- [ ] Test backup restoration
- [ ] Set retention policy (30 days)
- [ ] Monitor backup success

**Acceptance Criteria:**
- Backups run automatically daily
- Backups can be restored successfully
- Old backups automatically deleted

---

#### Task 4.4: Monitoring & Alerting
**Priority:** P1 (Important)
**Estimated Effort:** 8 hours
**Dependencies:** Phase 4 partial complete

**Subtasks:**
- [ ] Add Prometheus metrics endpoint:
  ```python
  from prometheus_flask_exporter import PrometheusMetrics
  metrics = PrometheusMetrics(app)
  ```

- [ ] Configure OpenShift monitoring
- [ ] Create Grafana dashboard
- [ ] Set up alerts:
  - High error rate
  - Slow response times
  - Database connection failures
  - High memory usage

**Acceptance Criteria:**
- Metrics collected and displayed
- Alerts fire for critical issues
- Dashboard shows key metrics

---

#### Task 4.5: Load Testing
**Priority:** P1 (Important)
**Estimated Effort:** 6 hours
**Dependencies:** Phase 1-3 complete

**Subtasks:**
- [ ] Create load test script with Locust:
  ```python
  from locust import HttpUser, task, between

  class TodoUser(HttpUser):
      wait_time = between(1, 3)

      @task(3)
      def get_todos(self):
          self.client.get('/api/todos')

      @task(1)
      def create_todo(self):
          self.client.post('/api/todos', json={'text': 'Load test todo'})
  ```

- [ ] Run tests with 100, 500, 1000 concurrent users
- [ ] Identify bottlenecks
- [ ] Optimize as needed
- [ ] Document performance baselines

**Acceptance Criteria:**
- App handles 1000 concurrent users
- 95th percentile response time < 200ms
- Error rate < 0.1%

---

#### Task 4.6: Security Audit
**Priority:** P0 (Blocker)
**Estimated Effort:** 8 hours
**Dependencies:** Phase 1-3 complete

**Subtasks:**
- [ ] Run OWASP ZAP security scan
- [ ] Fix SQL injection vulnerabilities (if any)
- [ ] Implement rate limiting:
  ```python
  from flask_limiter import Limiter
  limiter = Limiter(app, key_func=lambda: current_user.id)

  @app.route('/api/todos', methods=['POST'])
  @limiter.limit("10 per minute")
  def create_todo():
      # ...
  ```

- [ ] Add CSRF protection
- [ ] Audit dependencies for CVEs
- [ ] Enable security headers
- [ ] Implement input validation

**Acceptance Criteria:**
- Security scan passes with no high/critical issues
- Rate limiting prevents abuse
- CSRF tokens required for state-changing operations
- All dependencies up to date

---

#### Task 4.7: Horizontal Scaling Test
**Priority:** P1 (Important)
**Estimated Effort:** 4 hours
**Dependencies:** Task 2.5, Task 4.1

**Subtasks:**
- [ ] Scale to 3 replicas:
  ```bash
  oc scale deployment/todo-app --replicas=3
  ```

- [ ] Verify session sharing works
- [ ] Test database connection pooling
- [ ] Verify load balancing
- [ ] Monitor resource usage

**Acceptance Criteria:**
- Multiple replicas run successfully
- Sessions work across all pods
- Load distributed evenly
- No database connection issues

---

## Testing Strategy

### Unit Testing
- [ ] Add pytest framework
- [ ] Test models (CRUD operations)
- [ ] Test authentication logic
- [ ] Test API routes
- [ ] Achieve 80%+ code coverage

### Integration Testing
- [ ] Test database migrations
- [ ] Test OAuth flow end-to-end
- [ ] Test multi-user isolation
- [ ] Test session management

### End-to-End Testing
- [ ] Update Playwright tests for authentication
- [ ] Test full user workflow:
  1. Login
  2. Create todos
  3. Update todos
  4. Delete todos
  5. Logout
- [ ] Test on multiple browsers

### Performance Testing
- [ ] Load test with Locust
- [ ] Database query profiling
- [ ] Frontend performance audit
- [ ] API response time benchmarking

---

## Deployment Strategy

### Development Environment
1. Run locally with Docker Compose
2. Use local PostgreSQL and Redis
3. OAuth test credentials

### Staging Environment
1. Deploy to OpenShift staging project
2. Use staging database
3. Run full test suite
4. Performance testing

### Production Deployment
1. Database migration (zero-downtime)
2. Blue-green deployment
3. Gradual rollout (canary)
4. Monitor for errors
5. Rollback plan ready

### Rollback Plan
- [ ] Document rollback procedure
- [ ] Test rollback in staging
- [ ] Keep previous version deployable
- [ ] Database rollback scripts

---

## Success Criteria

### Phase 1 Success Criteria
- ✅ All todos persist across pod restarts
- ✅ Zero data loss during deployment
- ✅ API backward compatible
- ✅ Existing Playwright tests pass
- ✅ Can scale to 3+ replicas

### Phase 2 Success Criteria
- ✅ Users can log in with Google/GitHub
- ✅ Sessions persist across pod restarts
- ✅ Protected routes require authentication
- ✅ No security vulnerabilities

### Phase 3 Success Criteria
- ✅ Each user sees only their todos
- ✅ User statistics accurate
- ✅ Settings page functional
- ✅ Multi-user load test passes

### Phase 4 Success Criteria
- ✅ 99.9% uptime achieved
- ✅ < 200ms 95th percentile response time
- ✅ Handles 1000 concurrent users
- ✅ Security scan clean
- ✅ Automated backups running
- ✅ Monitoring dashboard complete

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data migration failure | Medium | High | Thorough testing, backup before migration |
| OAuth provider downtime | Low | Medium | Support multiple providers, graceful degradation |
| Database performance issues | Medium | High | Load testing, query optimization, caching |
| Session management bugs | Medium | Medium | Extensive integration testing |
| Security vulnerabilities | Medium | High | Security audit, dependency scanning |

---

## Timeline Estimate

**Total Effort:** 120-160 hours (3-4 months part-time)

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Database Foundation | 2 weeks | 30-40 hours |
| Phase 2: User Authentication | 2 weeks | 30-40 hours |
| Phase 3: Multi-User Support | 2 weeks | 20-30 hours |
| Phase 4: Production Hardening | 2 weeks | 40-50 hours |

**Target Completion:** End of Q1 2026

---

## Dependencies & Prerequisites

### External Dependencies
- PostgreSQL 13+ available on OpenShift
- Redis 6+ available on OpenShift
- OAuth credentials from Google/GitHub
- SSL certificates for HTTPS (provided by OpenShift)

### Team Requirements
- Backend developer (Python/Flask)
- Database administrator (PostgreSQL)
- DevOps engineer (OpenShift)
- QA engineer (testing)

### Infrastructure Requirements
- OpenShift cluster with persistent storage
- Minimum 2GB total memory allocation
- Database backup storage (50GB+)
- Monitoring stack (Prometheus/Grafana)

---

## Communication Plan

### Weekly Updates
- Monday: Sprint planning
- Wednesday: Mid-week sync
- Friday: Demo and retrospective

### Documentation
- Update PRD after each phase
- Maintain CHANGELOG.md
- Update CLAUDE.md with new procedures
- API documentation (Swagger/OpenAPI)

### Stakeholder Reviews
- End of Phase 1: Database migration review
- End of Phase 2: Authentication security review
- End of Phase 3: User acceptance testing
- End of Phase 4: Production readiness review

---

## Next Steps

1. **Immediate (This Week):**
   - [ ] Review and approve this task list
   - [ ] Set up local PostgreSQL for development
   - [ ] Begin Task 1.1: PostgreSQL Setup

2. **Short Term (Next 2 Weeks):**
   - [ ] Complete Phase 1 tasks
   - [ ] Run initial migration in staging
   - [ ] Validate data persistence

3. **Medium Term (1-2 Months):**
   - [ ] Complete Phases 2 and 3
   - [ ] User acceptance testing
   - [ ] Performance optimization

4. **Long Term (3-4 Months):**
   - [ ] Complete Phase 4
   - [ ] Production deployment
   - [ ] Post-launch monitoring

---

**Document Status:** Draft - Pending Approval
**Next Review Date:** TBD
**Owner:** Development Team
**Approver:** Product Manager

---

**End of Task List**
