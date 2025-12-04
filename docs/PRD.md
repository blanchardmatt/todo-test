# Product Requirements Document: Todo Application

**Version:** 1.0
**Last Updated:** December 2025
**Status:** Production
**Target Platform:** Red Hat OpenShift Container Platform

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [Technical Architecture](#technical-architecture)
4. [Functional Requirements](#functional-requirements)
5. [Non-Functional Requirements](#non-functional-requirements)
6. [API Specifications](#api-specifications)
7. [User Interface Specifications](#user-interface-specifications)
8. [Infrastructure & Deployment](#infrastructure--deployment)
9. [Testing Requirements](#testing-requirements)
10. [Security Requirements](#security-requirements)
11. [Known Limitations](#known-limitations)
12. [Future Considerations](#future-considerations)

---

## Executive Summary

The Todo Application is a lightweight, containerized task management web application designed for deployment on Red Hat OpenShift Container Platform. It provides a simple, intuitive interface for creating, managing, and tracking todo items with real-time updates and persistent session state.

**Key Characteristics:**
- Single-page application with zero external dependencies
- In-memory data storage (session-based)
- RESTful API architecture
- OpenShift-optimized containerization
- Automated testing with Playwright

---

## Product Overview

### Purpose
Provide a minimal, production-ready todo list application demonstrating:
- Modern web application architecture
- Container orchestration on OpenShift
- RESTful API design patterns
- Automated testing practices
- Security-hardened deployment

### Target Users
- Development teams learning OpenShift deployment
- Organizations requiring simple task tracking
- Educational institutions teaching containerization
- Developers prototyping Flask-based applications

### Success Metrics
- Application uptime: 99%+
- API response time: <100ms
- Zero security vulnerabilities in dependencies
- Successful automated test pass rate: 100%

---

## Technical Architecture

### Technology Stack

**Backend:**
- Python 3.9
- Flask 3.0.0 (Web framework)
- Werkzeug 3.0.1 (WSGI utilities)
- gunicorn 21.2.0 (WSGI server - included but not currently used)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 (embedded, no external frameworks)

**Infrastructure:**
- Red Hat UBI9 Python 3.9 base image
- OpenShift Container Platform
- Docker/Podman containerization

**Testing:**
- Playwright 1.56.0 (Browser automation)
- Chromium headless browser

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenShift Route                        │
│                   (HTTPS/TLS Termination)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   OpenShift Service                         │
│                   (ClusterIP: 8080)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Application Pod                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Flask Application                       │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  REST API Layer                                │ │  │
│  │  │  - GET /api/todos                              │ │  │
│  │  │  - POST /api/todos                             │ │  │
│  │  │  - PUT /api/todos/<id>                         │ │  │
│  │  │  - DELETE /api/todos/<id>                      │ │  │
│  │  │  - GET /health                                 │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  In-Memory Data Store                          │ │  │
│  │  │  - Python list: todos[]                        │ │  │
│  │  │  - Auto-incrementing ID counter                │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Static File Server                         │  │
│  │  - index.html (SPA)                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
.
├── src/                    # Application source code
│   ├── app.py              # Flask application entry point
│   └── templates/
│       └── index.html      # Single-page application UI
├── config/                 # Configuration files
│   ├── Dockerfile          # Container image definition
│   ├── openshift-deployment.yaml  # Kubernetes manifests
│   └── requirements.txt    # Python dependencies
├── tests/                  # Automated test suite
│   └── test_app.py         # Playwright end-to-end tests
├── output/                 # Test artifacts (gitignored)
│   └── .gitkeep
├── docs/                   # Documentation
│   └── PRD.md              # This document
├── run.py                  # Local development runner
├── CLAUDE.md               # Developer guide
├── README.md               # Project overview
└── .gitignore              # Git exclusions
```

---

## Functional Requirements

### FR-1: Todo Item Management

**FR-1.1: Create Todo**
- **Description:** Users can add new todo items
- **Input:** Text string (1-500 characters)
- **Processing:**
  - Assign unique auto-incrementing ID
  - Set `completed` status to `false`
  - Add to in-memory storage
- **Output:** HTTP 201 with created todo object
- **Validation:** Reject empty text strings with HTTP 400

**FR-1.2: View All Todos**
- **Description:** Users can view complete list of todos
- **Input:** None
- **Processing:** Retrieve all todos from storage
- **Output:** JSON array of todo objects
- **Sorting:** None (insertion order maintained)

**FR-1.3: Update Todo**
- **Description:** Users can modify todo text or completion status
- **Input:** Todo ID + updates (text and/or completed flag)
- **Processing:**
  - Locate todo by ID
  - Update specified fields
- **Output:** HTTP 200 with updated todo object
- **Error Handling:** HTTP 404 if ID not found

**FR-1.4: Delete Todo**
- **Description:** Users can remove todo items
- **Input:** Todo ID
- **Processing:** Remove from storage by ID
- **Output:** HTTP 200 with deleted todo object
- **Error Handling:** HTTP 404 if ID not found

**FR-1.5: Toggle Completion Status**
- **Description:** Users can mark todos as complete/incomplete
- **Input:** Todo ID + checkbox state
- **Processing:** Update `completed` boolean via PUT request
- **Output:** Updated todo object
- **UI Effect:**
  - Strikethrough text styling
  - Reduced opacity (60%)
  - Updated task counter

### FR-2: User Interface

**FR-2.1: Todo Input**
- **Component:** Text input field
- **Placeholder:** "What needs to be done?"
- **Auto-focus:** Yes (on page load)
- **Interaction:**
  - Click "Add" button → Create todo
  - Press Enter key → Create todo
  - Clear input after submission

**FR-2.2: Todo List Display**
- **Component:** Unordered list
- **Item Layout:**
  ```
  [Checkbox] Todo text here                [Delete]
  ```
- **Empty State:** "No tasks yet. Add one above!"
- **Styling:**
  - Light gray background (#f8f9fa)
  - Rounded corners (8px)
  - Hover effect: Translate right 5px
  - Completed items: Strikethrough + gray text

**FR-2.3: Task Statistics**
- **Component:** Status bar at bottom
- **Display:** "{N} task(s) remaining"
- **Calculation:** Count of todos where `completed = false`
- **Update Trigger:** Any todo modification

**FR-2.4: Visual Design**
- **Color Scheme:**
  - Background gradient: Purple (#667eea) to violet (#764ba2)
  - Container: White with shadow
  - Primary button: Blue (#667eea)
  - Delete button: Red (#dc3545)
- **Typography:** System font stack (SF Pro, Segoe UI, Roboto)
- **Responsive:** Max width 600px, centered

### FR-3: Health Monitoring

**FR-3.1: Health Check Endpoint**
- **Endpoint:** `GET /health`
- **Response:** `{"status": "healthy"}`
- **HTTP Status:** 200 OK
- **Purpose:** OpenShift liveness/readiness probes
- **Check Interval:** Every 10 seconds (liveness), 5 seconds (readiness)

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1: Response Time**
- API endpoints: < 50ms (95th percentile)
- Page load: < 500ms (first contentful paint)
- UI interactions: < 100ms response

**NFR-1.2: Scalability**
- Single replica deployment (in-memory storage limitation)
- Supports 100+ concurrent users per pod
- Handles 1000+ todos per session

**NFR-1.3: Resource Usage**
- Memory: < 128Mi under normal load
- CPU: < 100m under normal load
- No resource requests/limits set (uses OpenShift defaults)

### NFR-2: Reliability

**NFR-2.1: Availability**
- Target: 99.9% uptime
- Health checks every 5-10 seconds
- Automatic pod restart on failure
- Initial delay: 30s liveness, 5s readiness

**NFR-2.2: Error Handling**
- Graceful degradation for API failures
- Console logging for debugging
- User-friendly error messages (future enhancement)

### NFR-3: Security

**NFR-3.1: Transport Security**
- HTTPS enforced via OpenShift Route
- TLS termination at edge
- HTTP → HTTPS redirect

**NFR-3.2: Input Validation**
- XSS protection via HTML escaping in frontend
- Content-Type validation (application/json)
- Text input sanitization

**NFR-3.3: Container Security**
- Non-root user execution (OpenShift requirement)
- Arbitrary user ID support (1000660000+)
- No privilege escalation
- Read-only root filesystem compatible

### NFR-4: Maintainability

**NFR-4.1: Code Quality**
- Single-file backend (app.py: ~75 LOC)
- Single-file frontend (index.html: ~270 LOC)
- Zero external JavaScript dependencies
- Inline CSS (no build process required)

**NFR-4.2: Documentation**
- Comprehensive CLAUDE.md for developers
- PRD for product specification
- Inline code comments for complex logic
- OpenShift deployment examples

---

## API Specifications

### Base URL
- **Local Development:** `http://localhost:8080`
- **Production:** `https://<route-url>` (OpenShift-provided)

### Endpoints

#### 1. List All Todos
```http
GET /api/todos
```

**Response:**
```json
[
  {
    "id": 1,
    "text": "Buy groceries",
    "completed": false
  },
  {
    "id": 2,
    "text": "Finish report",
    "completed": true
  }
]
```

**Status Codes:**
- `200 OK`: Success

---

#### 2. Create Todo
```http
POST /api/todos
Content-Type: application/json

{
  "text": "New todo item"
}
```

**Response:**
```json
{
  "id": 3,
  "text": "New todo item",
  "completed": false
}
```

**Status Codes:**
- `201 Created`: Todo created successfully
- `400 Bad Request`: Missing or empty text field

**Validation:**
- `text` field is required
- `text` must be non-empty string

---

#### 3. Update Todo
```http
PUT /api/todos/{id}
Content-Type: application/json

{
  "completed": true,
  "text": "Updated text (optional)"
}
```

**Response:**
```json
{
  "id": 1,
  "text": "Updated text",
  "completed": true
}
```

**Status Codes:**
- `200 OK`: Todo updated successfully
- `404 Not Found`: Todo ID does not exist

**Notes:**
- Both `completed` and `text` fields are optional
- Only provided fields are updated

---

#### 4. Delete Todo
```http
DELETE /api/todos/{id}
```

**Response:**
```json
{
  "id": 1,
  "text": "Deleted todo",
  "completed": false
}
```

**Status Codes:**
- `200 OK`: Todo deleted successfully
- `404 Not Found`: Todo ID does not exist

---

#### 5. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK`: Application is healthy

**Purpose:** Used by OpenShift for liveness and readiness probes

---

### Data Model

#### Todo Object
```typescript
{
  id: number;           // Auto-incrementing integer (starts at 1)
  text: string;         // Todo description
  completed: boolean;   // Completion status
}
```

**Storage:**
- Python list: `todos = []`
- Counter: `todo_id_counter = 1` (global, increments on create)
- Persistence: In-memory only (lost on pod restart)

---

## User Interface Specifications

### Layout

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                   My Todo List                         │
│                                                        │
│  ┌──────────────────────────────────────┐  ┌─────┐   │
│  │ What needs to be done?               │  │ Add │   │
│  └──────────────────────────────────────┘  └─────┘   │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☐ Buy groceries                       [Delete] │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☑ Finish report                       [Delete] │  │ (completed)
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☐ Call dentist                        [Delete] │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  ─────────────────────────────────────────────────   │
│                2 tasks remaining                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Component Specifications

#### 1. Header
- **Text:** "My Todo List"
- **Font Size:** 2.5em
- **Alignment:** Center
- **Color:** #333 (dark gray)
- **Margin:** 30px bottom

#### 2. Input Container
- **Display:** Flex row
- **Gap:** 10px
- **Margin:** 30px bottom

**Input Field:**
- **ID:** `todoInput`
- **Type:** text
- **Placeholder:** "What needs to be done?"
- **Padding:** 15px
- **Border:** 2px solid #e0e0e0
- **Border Radius:** 8px
- **Font Size:** 16px
- **Focus State:** Border color #667eea

**Add Button:**
- **ID:** `addBtn`
- **Text:** "Add"
- **Padding:** 15px 30px
- **Background:** #667eea
- **Color:** White
- **Border:** None
- **Border Radius:** 8px
- **Font Weight:** 600
- **Hover State:** Background #5568d3

#### 3. Todo List
- **ID:** `todoList`
- **Type:** `<ul>` (unordered list)
- **List Style:** None

**Todo Item:**
- **Class:** `todo-item` (+ `completed` if done)
- **Display:** Flex row
- **Align Items:** Center
- **Padding:** 15px
- **Margin:** 10px bottom
- **Background:** #f8f9fa
- **Border Radius:** 8px
- **Hover Effect:**
  - Background: #e9ecef
  - Transform: translateX(5px)
- **Transition:** all 0.3s

**Checkbox:**
- **Type:** checkbox
- **Size:** 20px × 20px
- **Margin:** 15px right
- **Cursor:** pointer
- **onChange:** `toggleTodo(id, checked)`

**Text Span:**
- **Class:** `todo-text`
- **Flex:** 1 (fills space)
- **Font Size:** 16px
- **Color:** #333
- **Completed State:**
  - Text Decoration: line-through
  - Color: #999

**Delete Button:**
- **Class:** `delete-btn`
- **Text:** "Delete"
- **Padding:** 8px 15px
- **Background:** #dc3545 (red)
- **Color:** White
- **Border:** None
- **Border Radius:** 5px
- **Font Size:** 14px
- **Cursor:** pointer
- **Hover State:** Background #c82333
- **onClick:** `deleteTodo(id)`

#### 4. Empty State
- **Class:** `empty-state`
- **Text:** "No tasks yet. Add one above!"
- **Alignment:** Center
- **Color:** #999
- **Padding:** 40px
- **Font Size:** 18px

#### 5. Statistics Bar
- **Class:** `stats`
- **Margin:** 30px top
- **Padding:** 20px top
- **Border Top:** 2px solid #e0e0e0
- **Text Align:** Center
- **Color:** #666
- **Font Size:** 14px

**Text Format:**
- Single task: "1 task remaining"
- Multiple/zero: "{N} tasks remaining"

### JavaScript Functions

#### Core Functions

```javascript
async function loadTodos()
// Fetches all todos from API and renders them
// Called on: Page load, after any modification

async function addTodo()
// Creates new todo from input value
// Validation: Trims whitespace, rejects empty strings
// Called on: Button click, Enter key press

async function toggleTodo(id, completed)
// Updates todo completion status
// Parameters: id (number), completed (boolean)
// Called on: Checkbox change event

async function deleteTodo(id)
// Removes todo from list
// Parameters: id (number)
// Called on: Delete button click

function renderTodos(todos)
// Updates DOM with todo list
// Parameters: todos (array)
// Handles: Empty state, task counter, HTML escaping

function escapeHtml(text)
// Prevents XSS by escaping HTML entities
// Parameters: text (string)
// Returns: Sanitized HTML string
```

#### Event Listeners

```javascript
// Add button click
addBtn.addEventListener('click', addTodo);

// Enter key in input
todoInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') addTodo();
});

// Checkbox toggle (inline)
onchange="toggleTodo(${todo.id}, this.checked)"

// Delete button (inline)
onclick="deleteTodo(${todo.id})"
```

---

## Infrastructure & Deployment

### Container Image

**Dockerfile:**
```dockerfile
FROM registry.access.redhat.com/ubi9/python-39:latest

WORKDIR /app

COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py .
COPY src/templates/ templates/

EXPOSE 8080
ENV PORT=8080

CMD ["python", "app.py"]
```

**Critical Notes:**
- **NO `chmod` commands** - Fails in OpenShift builds due to permissions
- Uses Red Hat UBI (Universal Base Image) for OpenShift compatibility
- Base image handles arbitrary user ID permissions automatically
- Port 8080 is OpenShift standard for applications

### OpenShift Deployment

**Deployment Manifest:** `config/openshift-deployment.yaml`

**Key Components:**

1. **Deployment:**
   - Replicas: 1 (in-memory storage limitation)
   - Image: `todo-app:latest`
   - Port: 8080
   - No resource limits/requests (uses cluster defaults)
   - Liveness probe: `/health`, 30s initial delay, 10s period
   - Readiness probe: `/health`, 5s initial delay, 5s period

2. **Service:**
   - Type: ClusterIP
   - Port: 8080
   - Target Port: 8080

3. **Route:**
   - TLS Termination: Edge
   - Insecure Traffic: Redirect to HTTPS
   - Target: Service port `http`

### Deployment Methods

**Method 1: Source-to-Image (S2I) - Recommended**
```bash
oc new-app python:3.9~https://github.com/blanchardmatt/todo-test.git --name=todo-app
oc expose svc/todo-app
```

**Method 2: Docker Build**
```bash
oc new-build --name=todo-app --binary --strategy=docker -f config/Dockerfile
oc start-build todo-app --from-dir=. --follow
oc apply -f config/openshift-deployment.yaml
```

### Environment Variables

- `PORT`: Application listen port (default: 8080)

### Build Requirements

**OpenShift Quota Considerations:**
- Different OpenShift clusters have different resource quotas
- Resource limits removed from deployment to use cluster defaults
- Typical constraints encountered:
  - Minimum CPU: 129m
  - Maximum Memory: 1512Mi

**Solution:** Let OpenShift assign defaults rather than explicit limits

---

## Testing Requirements

### Automated Testing

**Framework:** Playwright (Python)
**Browser:** Chromium (headless)
**Test File:** `tests/test_app.py`

### Test Cases

#### TC-1: Application Launch
- **Test:** Browser can load application
- **Validation:** Page title is "Todo App"

#### TC-2: Add Todo
- **Test:** Create new todo item
- **Steps:**
  1. Fill input: "Test todo item from Playwright"
  2. Click "Add" button
- **Validation:** Todo appears in list with correct text

#### TC-3: Mark Complete
- **Test:** Toggle todo completion status
- **Steps:**
  1. Click checkbox on first todo
- **Validation:** Checkbox is checked

#### TC-4: Add Multiple Todos
- **Test:** Create second todo item
- **Steps:**
  1. Fill input: "Second test todo"
  2. Click "Add" button
- **Validation:** Todo count is 2

#### TC-5: Delete Todo
- **Test:** Remove todo from list
- **Steps:**
  1. Click "Delete" on first todo
- **Validation:** Remaining count is 1

#### TC-6: Task Statistics
- **Test:** Verify counter accuracy
- **Steps:**
  1. Check stats text
- **Validation:** Displays "1 task remaining"

#### TC-7: Screenshot Capture
- **Test:** Visual regression baseline
- **Steps:**
  1. Capture screenshot
- **Output:** `output/test_screenshot.png`

### Test Execution

```bash
# Install dependencies
pip install playwright
python -m playwright install chromium

# Run tests
cd tests && python test_app.py
```

**Expected Output:**
```
[PASS] Browser launched
[PASS] Navigated to http://localhost:8080
[PASS] Page title: Todo App
[PASS] Todo added: Test todo item from Playwright
[PASS] Todo marked as completed: True
[PASS] Total todos: 2
[PASS] Remaining todos after deletion: 1
[PASS] Stats display: 1 task remaining
[PASS] Screenshot saved as ../output/test_screenshot.png
[SUCCESS] All tests completed successfully!
```

### Manual Testing

**Health Check:**
```bash
curl http://localhost:8080/health
# Expected: {"status":"healthy"}
```

**API Test:**
```bash
# List todos
curl http://localhost:8080/api/todos

# Create todo
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"text":"Test todo"}'
```

---

## Security Requirements

### SEC-1: Authentication & Authorization
- **Current State:** None implemented
- **Future Consideration:** Add user authentication for multi-user scenarios

### SEC-2: Input Validation
- **XSS Protection:**
  - Frontend: `escapeHtml()` function sanitizes all user input
  - Backend: Flask's `jsonify()` handles JSON encoding
- **SQL Injection:** N/A (no database)
- **Request Validation:**
  - Content-Type checking
  - JSON parsing error handling

### SEC-3: Transport Security
- **HTTPS:** Enforced via OpenShift Route
- **TLS Version:** 1.2+ (managed by OpenShift)
- **Certificate:** Auto-managed by OpenShift
- **HTTP Redirect:** Automatic (insecureEdgeTerminationPolicy: Redirect)

### SEC-4: Container Security
- **Non-Root User:** Required by OpenShift (arbitrary UID 1000660000+)
- **Base Image:** Red Hat UBI (security-patched, maintained)
- **Secrets:** None used (stateless application)
- **Capabilities:** None required

### SEC-5: Dependency Security
- **Python Packages:**
  - Flask 3.0.0 (no known CVEs)
  - Werkzeug 3.0.1 (security utilities)
  - gunicorn 21.2.0
- **Update Policy:** Monitor for security advisories, update quarterly

### SEC-6: CORS Policy
- **Current State:** No CORS headers (same-origin only)
- **Future Consideration:** Add CORS for API-only deployments

---

## Known Limitations

### LIMIT-1: Data Persistence
- **Issue:** Todos stored in-memory only
- **Impact:** Data lost on pod restart/redeployment
- **Workaround:** None currently
- **Future Fix:** Implement database backend (PostgreSQL/MongoDB)

### LIMIT-2: Single Replica
- **Issue:** Cannot scale horizontally (no shared state)
- **Impact:** Limited to single pod deployment
- **Workaround:** Use database for multi-replica support
- **Future Fix:** Add persistent storage layer

### LIMIT-3: No User Authentication
- **Issue:** Single shared todo list for all users
- **Impact:** Not suitable for multi-tenant deployments
- **Workaround:** Deploy separate instances per user
- **Future Fix:** Add user authentication and authorization

### LIMIT-4: No Real-Time Sync
- **Issue:** Changes not synchronized across browser tabs
- **Impact:** Users must refresh to see updates from other tabs
- **Workaround:** Manual page refresh
- **Future Fix:** Implement WebSocket or SSE for live updates

### LIMIT-5: No Data Export
- **Issue:** Cannot export todo list
- **Impact:** No backup or migration capability
- **Workaround:** Manual copy/paste
- **Future Fix:** Add CSV/JSON export feature

### LIMIT-6: No Task Priority
- **Issue:** All todos equal priority
- **Impact:** Cannot organize by importance
- **Workaround:** Use numbering in text (e.g., "1. High priority task")
- **Future Fix:** Add priority levels (high/medium/low)

### LIMIT-7: No Due Dates
- **Issue:** No deadline tracking
- **Impact:** Cannot sort by urgency
- **Workaround:** Include dates in text
- **Future Fix:** Add date picker for due dates

---

## Future Considerations

### Phase 2 Enhancements

**Database Integration:**
- PostgreSQL for relational data
- Redis for session management
- Migration scripts for data import

**User Management:**
- OAuth 2.0 authentication (Google, GitHub)
- User registration/login
- Per-user todo lists
- Sharing and collaboration features

**Advanced Features:**
- Task categories/tags
- Due dates and reminders
- Priority levels (high/medium/low)
- Subtasks (nested todos)
- Rich text descriptions
- File attachments
- Search and filter

**UI/UX Improvements:**
- Drag-and-drop reordering
- Bulk operations (select multiple, delete all completed)
- Keyboard shortcuts
- Dark mode theme
- Mobile-responsive design
- Progressive Web App (PWA)

**API Enhancements:**
- Pagination for large lists
- Sorting and filtering endpoints
- Batch operations
- GraphQL alternative
- API versioning (v2)
- Rate limiting

**DevOps:**
- CI/CD pipeline (GitHub Actions)
- Automated security scanning
- Performance monitoring (Prometheus)
- Centralized logging (ELK stack)
- Multi-environment deployments (dev/staging/prod)

**Testing:**
- Unit tests for backend
- Integration tests for API
- Visual regression tests
- Load testing (k6, Locust)
- Accessibility testing (WCAG 2.1)

---

## Appendix A: Development Setup

### Prerequisites
- Python 3.9+
- pip package manager
- Git

### Local Development
```bash
# Clone repository
git clone https://github.com/blanchardmatt/todo-test.git
cd todo-test

# Install dependencies
pip install -r config/requirements.txt

# Run application
python run.py

# Access at http://localhost:8080
```

### Testing Setup
```bash
# Install Playwright
pip install playwright
python -m playwright install chromium

# Run tests
cd tests
python test_app.py

# View screenshots
open ../output/test_screenshot.png
```

---

## Appendix B: Troubleshooting

### Issue: Port 8080 Already in Use
```bash
# Find process using port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Kill process or use different port
PORT=3000 python run.py
```

### Issue: OpenShift Build Fails - chmod Error
**Error:** `chmod: changing permissions of '/app': Operation not permitted`

**Solution:** Remove `chmod` commands from Dockerfile (UBI handles permissions)

### Issue: OpenShift Resource Quota Exceeded
**Error:** `minimum cpu usage per Pod is 129m, but request is 100m`

**Solution:** Remove resource limits from `openshift-deployment.yaml` or adjust to cluster quotas

### Issue: Health Check Failing
**Symptoms:** Pod restarting continuously

**Diagnosis:**
```bash
oc logs -f deployment/todo-app
oc describe pod <pod-name>
```

**Common Causes:**
- Application not binding to 0.0.0.0
- Port mismatch (ensure 8080)
- Initial delay too short (increase to 30s)

---

## Appendix C: API Testing Examples

### cURL Examples

**Create Todo:**
```bash
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"text":"Buy milk"}'
```

**List Todos:**
```bash
curl http://localhost:8080/api/todos | jq .
```

**Update Todo:**
```bash
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

**Delete Todo:**
```bash
curl -X DELETE http://localhost:8080/api/todos/1
```

### Postman Collection
(Future: Export Postman collection to `docs/postman_collection.json`)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Claude Code | Initial PRD creation |

---

**End of Product Requirements Document**
