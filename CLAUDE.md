# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask-based todo application designed to run on Red Hat OpenShift Container Platform. It uses in-memory storage and provides a RESTful API with a web interface.

## Project Structure

```
.
├── src/                    # Source code
│   ├── app.py              # Main Flask application
│   └── templates/          # HTML templates
│       └── index.html      # Frontend UI
├── config/                 # Configuration files
│   ├── Dockerfile          # Container definition
│   ├── openshift-deployment.yaml  # OpenShift configuration
│   └── requirements.txt    # Python dependencies
├── tests/                  # Test files
│   └── test_app.py         # Playwright tests
├── output/                 # Test results and screenshots
├── run.py                  # Convenience script to run app from root
└── CLAUDE.md               # This file
```

## Development Commands

### Local Development

```bash
# Install dependencies
pip install -r config/requirements.txt

# Run the application locally (from root)
python run.py

# Or run directly from src folder
cd src && python app.py
```

The application runs on `http://localhost:8080` by default.

### Testing

```bash
# Install Playwright
pip install playwright
python -m playwright install chromium

# Run tests
cd tests && python test_app.py

# Test results and screenshots saved to output/
```

### OpenShift Deployment

```bash
# Method 1: Source-to-Image (S2I) - Recommended
oc new-app python:3.9~<git-repo-url> --name=todo-app
oc expose svc/todo-app

# Method 2: Docker Build
oc new-build --name=todo-app --binary --strategy=docker -f config/Dockerfile
oc start-build todo-app --from-dir=. --follow
oc apply -f config/openshift-deployment.yaml

# Common operations
oc get pods                          # Check pod status
oc logs -f deployment/todo-app       # View application logs
oc describe pod <pod-name>           # Detailed pod information
oc get route todo-app                # Get application URL
```

## Architecture

### Application Structure

- **[src/app.py](src/app.py)**: Main Flask application with all route handlers and business logic
- **[src/templates/index.html](src/templates/index.html)**: Single-page application with vanilla JavaScript, embedded CSS, and full frontend logic
- **[config/Dockerfile](config/Dockerfile)**: Container definition using Red Hat UBI9 Python 3.9 base image
- **[config/openshift-deployment.yaml](config/openshift-deployment.yaml)**: Complete OpenShift configuration (Deployment, Service, Route)
- **[tests/test_app.py](tests/test_app.py)**: Playwright automated tests for the application

### Data Storage

Todos are stored in-memory using a global Python list in [src/app.py](src/app.py:8). This means:
- Data is lost on pod restart or redeployment
- No database or persistent storage is configured
- Thread-safe operations are not implemented (single-threaded Flask development server)

If persistent storage is needed, implement a database backend (PostgreSQL or MongoDB) to replace the `todos` list.

### API Design

All API endpoints are defined in [src/app.py](src/app.py) and follow RESTful conventions:
- `GET /api/todos` - List all todos
- `POST /api/todos` - Create todo (requires `{"text": "..."}`)
- `PUT /api/todos/<id>` - Update todo (accepts `completed` and `text` fields)
- `DELETE /api/todos/<id>` - Delete todo
- `GET /health` - Health check for OpenShift probes

Frontend JavaScript in [src/templates/index.html](src/templates/index.html:165-270) handles all API interactions using fetch.

### OpenShift Integration

The application is configured for OpenShift with:
- Non-root user support (required by OpenShift security policies)
- Health probes on `/health` endpoint (liveness and readiness)
- Edge TLS termination via OpenShift Route
- Resource limits: 128Mi-256Mi memory, 100m-500m CPU

Key OpenShift-specific considerations:
- Uses Red Hat UBI (Universal Base Image) for compatibility
- Port 8080 is the default OpenShift application port
- Container runs with arbitrary user ID assigned by OpenShift
- File permissions set with `chmod -R g+rwX` to support group access

## Configuration

### Environment Variables

- `PORT`: Application port (default: 8080)

### Dependencies

- Flask 3.0.0: Web framework
- Werkzeug 3.0.1: WSGI utilities
- gunicorn 21.2.0: Production WSGI server (included but not currently used, runs with `python app.py`)

## Testing the Application

### Automated Testing

Run the Playwright test suite:

```bash
cd tests && python test_app.py
```

The tests will verify:
- Adding new todos
- Marking todos as complete
- Deleting todos
- Task statistics

Screenshots are saved to the [output/](output/) folder.

### Manual Testing

You can also manually test using curl:

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test API endpoints
curl http://localhost:8080/api/todos
curl -X POST http://localhost:8080/api/todos -H "Content-Type: application/json" -d '{"text":"Test todo"}'
```

## Security Notes

- Container runs as non-root user per OpenShift requirements
- HTTPS enforced via OpenShift Route with edge TLS termination
- No authentication or authorization implemented
- XSS protection via HTML escaping in frontend ([src/templates/index.html](src/templates/index.html:265-269))
