# Todo Application for OpenShift

A simple, containerized Python Flask todo application designed to run on Red Hat OpenShift Container Platform.

## Features

- Add, complete, and delete todos
- Clean, responsive web interface
- RESTful API
- Health check endpoint for OpenShift
- Persistent deployment configuration

## Project Structure

```
.
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Frontend interface
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── openshift-deployment.yaml  # OpenShift deployment configuration
└── README.md                  # This file
```

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to: `http://localhost:8080`

## Deploying to OpenShift

### Method 1: Using Source-to-Image (S2I) - Recommended

1. Login to your OpenShift cluster:
```bash
oc login <your-openshift-cluster-url>
```

2. Create a new project (optional):
```bash
oc new-project todo-app
```

3. Create a new app from source:
```bash
oc new-app python:3.9~https://github.com/<your-username>/<your-repo>.git --name=todo-app
```

4. Expose the service:
```bash
oc expose svc/todo-app
```

5. Get the route URL:
```bash
oc get route todo-app
```

### Method 2: Using Docker Build

1. Login to OpenShift:
```bash
oc login <your-openshift-cluster-url>
```

2. Create a new project (optional):
```bash
oc new-project todo-app
```

3. Create a new build configuration:
```bash
oc new-build --name=todo-app --binary --strategy=docker
```

4. Start the build from local directory:
```bash
oc start-build todo-app --from-dir=. --follow
```

5. Deploy the application:
```bash
oc apply -f openshift-deployment.yaml
```

6. Get the route URL:
```bash
oc get route todo-app
```

### Method 3: Using Pre-built Image

If you have the image pushed to a registry:

1. Login to OpenShift:
```bash
oc login <your-openshift-cluster-url>
```

2. Create a new project (optional):
```bash
oc new-project todo-app
```

3. Apply the deployment configuration:
```bash
oc apply -f openshift-deployment.yaml
```

4. Update the image reference if needed:
```bash
oc set image deployment/todo-app todo-app=<your-registry>/todo-app:latest
```

5. Get the route URL:
```bash
oc get route todo-app
```

## API Endpoints

- `GET /` - Web interface
- `GET /api/todos` - Get all todos
- `POST /api/todos` - Create a new todo
  - Body: `{"text": "Todo text"}`
- `PUT /api/todos/<id>` - Update a todo
  - Body: `{"completed": true/false}`
- `DELETE /api/todos/<id>` - Delete a todo
- `GET /health` - Health check endpoint

## Configuration

### Environment Variables

- `PORT` - Port number (default: 8080)

### Resource Limits

Default resource limits in OpenShift deployment:
- Memory: 128Mi (request) / 256Mi (limit)
- CPU: 100m (request) / 500m (limit)

Adjust these in [openshift-deployment.yaml](openshift-deployment.yaml) based on your needs.

## Health Checks

The application includes:
- **Liveness probe**: Checks `/health` endpoint every 10 seconds
- **Readiness probe**: Checks `/health` endpoint every 5 seconds

## Security Considerations

- The container runs as a non-root user (OpenShift requirement)
- HTTPS is enforced via OpenShift Route with edge TLS termination
- No persistent storage - todos are stored in memory (restart will clear data)

## Troubleshooting

### Check pod status:
```bash
oc get pods
```

### View logs:
```bash
oc logs -f deployment/todo-app
```

### Describe pod for events:
```bash
oc describe pod <pod-name>
```

### Check route:
```bash
oc get route todo-app -o jsonpath='{.spec.host}'
```

## Future Enhancements

- Add persistent storage (PostgreSQL or MongoDB)
- Implement user authentication
- Add task categories/tags
- Due dates and reminders
- Export/import functionality

## License

MIT License - feel free to use this for your university project!
