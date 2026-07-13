# SSE Transport Setup Guide

This guide explains how to run the SevOne MCP Server with SSE (Server-Sent Events) transport for remote access.

## When to Use SSE

Use SSE transport when you need:
- Remote access from different machines
- Multiple Bob instances sharing one server
- Centralized server management
- Container/cloud deployment
- Enterprise monitoring and logging

For local, single-user scenarios, use the stdio transport (default).

See [TRANSPORT_COMPARISON.md](TRANSPORT_COMPARISON.md) for detailed comparison.

## Installation

### 1. Install SSE Dependencies

```bash
pip install -r requirements-sse.txt
```

This installs additional packages:
- `starlette` - ASGI web framework
- `uvicorn` - ASGI server
- `sse-starlette` - SSE support

### 2. Configure Environment

Same `.env` file as stdio version:

```bash
SEVONE_HOSTNAME=your-sevone-hostname.com
SEVONE_USERNAME=your-username
SEVONE_PASSWORD_ENCRYPTED=<encrypted-password>
SEVONE_ENCRYPTION_KEY=<encryption-key>
SEVONE_VERIFY_SSL=false
LOG_LEVEL=INFO
```

## Running the SSE Server

### Basic Usage

```bash
python src/server_sse.py
```

Default: `http://0.0.0.0:8444`

### Custom Host/Port

```bash
python src/server_sse.py --host 127.0.0.1 --port 9000
```

### Production Deployment

```bash
# With specific host and port
python src/server_sse.py --host 0.0.0.0 --port 8444

# The server will log:
# ✓ Successfully authenticated with SevOne
# ✓ SevOne MCP Server ready
# Starting SSE server on 0.0.0.0:8444
# SSE endpoint: http://0.0.0.0:8444/sse
# Messages endpoint: http://0.0.0.0:8444/messages
```

## Bob Configuration

### For SSE Transport

Add to Bob's MCP configuration:

```json
{
  "mcpServers": {
    "sevone-api": {
      "transport": "sse",
      "url": "http://localhost:8444/sse",
      "timeout": 30000
    }
  }
}
```

### For Remote Server

```json
{
  "mcpServers": {
    "sevone-api": {
      "transport": "sse",
      "url": "http://sevone-mcp-server.example.com:8444/sse",
      "headers": {
        "Authorization": "Bearer your-auth-token"
      },
      "timeout": 30000
    }
  }
}
```

## Security Considerations

### 1. Network Exposure

The SSE server exposes HTTP endpoints. Consider:

- **Firewall**: Restrict access to trusted IPs
- **VPN**: Run on private network
- **Reverse Proxy**: Use nginx/Apache with SSL
- **Authentication**: Add auth middleware (see below)

### 2. Add Authentication (Optional)

Create `src/middleware/auth.py`:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check for auth token
        auth_header = request.headers.get("Authorization")
        expected_token = os.getenv("MCP_AUTH_TOKEN")
        
        if expected_token and auth_header != f"Bearer {expected_token}":
            return JSONResponse(
                {"error": "Unauthorized"},
                status_code=401
            )
        
        return await call_next(request)
```

Add to `.env`:
```bash
MCP_AUTH_TOKEN=your-secure-token-here
```

Update `server_sse.py`:
```python
from middleware.auth import AuthMiddleware

def create_app():
    app = Starlette(routes=[...])
    app.add_middleware(AuthMiddleware)
    return app
```

### 3. SSL/TLS

For production, use HTTPS:

```bash
# Generate self-signed cert (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with SSL
uvicorn src.server_sse:create_app --host 0.0.0.0 --port 8444 \
  --ssl-keyfile key.pem --ssl-certfile cert.pem
```

Bob configuration:
```json
{
  "mcpServers": {
    "sevone-api": {
      "transport": "sse",
      "url": "https://localhost:8444/sse"
    }
  }
}
```

## Container Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt requirements-sse.txt ./
RUN pip install --no-cache-dir -r requirements-sse.txt

# Copy source
COPY src/ ./src/
COPY .env ./

# Expose port
EXPOSE 8444

# Run SSE server
CMD ["python", "src/server_sse.py", "--host", "0.0.0.0", "--port", "8444"]
```

### Build and Run

```bash
# Build
docker build -t sevone-mcp-sse .

# Run
docker run -d \
  --name sevone-mcp \
  -p 8444:8444 \
  --env-file .env \
  sevone-mcp-sse

# Check logs
docker logs -f sevone-mcp
```

### Docker Compose

```yaml
version: '3.8'

services:
  sevone-mcp:
    build: .
    ports:
      - "8444:8444"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8444/sse"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run:
```bash
docker-compose up -d
```

## Kubernetes Deployment

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sevone-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sevone-mcp
  template:
    metadata:
      labels:
        app: sevone-mcp
    spec:
      containers:
      - name: sevone-mcp
        image: sevone-mcp-sse:latest
        ports:
        - containerPort: 8444
        env:
        - name: SEVONE_HOSTNAME
          valueFrom:
            secretKeyRef:
              name: sevone-credentials
              key: hostname
        - name: SEVONE_USERNAME
          valueFrom:
            secretKeyRef:
              name: sevone-credentials
              key: username
        - name: SEVONE_PASSWORD_ENCRYPTED
          valueFrom:
            secretKeyRef:
              name: sevone-credentials
              key: password-encrypted
        - name: SEVONE_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: sevone-credentials
              key: encryption-key
---
apiVersion: v1
kind: Service
metadata:
  name: sevone-mcp
spec:
  selector:
    app: sevone-mcp
  ports:
  - port: 8444
    targetPort: 8444
  type: LoadBalancer
```

## Monitoring

### Health Check Endpoint

Add to `server_sse.py`:

```python
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "server": "sevone-mcp-sse",
        "version": "1.0.0"
    })

# Add route
Route("/health", endpoint=health_check)
```

### Prometheus Metrics

Install:
```bash
pip install prometheus-client
```

Add metrics:
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('mcp_requests_total', 'Total requests')
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration')

async def metrics(request):
    return Response(generate_latest(), media_type="text/plain")

# Add route
Route("/metrics", endpoint=metrics)
```

## Load Balancing

### nginx Configuration

```nginx
upstream sevone_mcp {
    server localhost:8444;
    server localhost:8445;
    server localhost:8446;
}

server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://sevone_mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8444

# Kill process
kill -9 <PID>

# Or use different port
python src/server_sse.py --port 9000
```

### Connection Refused

1. Check server is running: `curl http://localhost:8444/sse`
2. Check firewall rules
3. Verify Bob configuration URL matches server

### Authentication Errors

1. Check `.env` credentials
2. Verify SevOne API is accessible
3. Check logs: `LOG_LEVEL=DEBUG`

## Performance Tuning

### Uvicorn Workers

```bash
# Multiple workers for production
uvicorn src.server_sse:create_app \
  --host 0.0.0.0 \
  --port 8444 \
  --workers 4 \
  --log-level info
```

### Connection Limits

```python
# In server_sse.py
config = uvicorn.Config(
    app,
    host=args.host,
    port=args.port,
    limit_concurrency=100,
    limit_max_requests=10000
)
```

## Comparison: stdio vs SSE

| Feature | stdio | SSE |
|---------|-------|-----|
| Setup | Simple | Moderate |
| Remote Access | ❌ | ✅ |
| Multi-Client | ❌ | ✅ |
| Port Required | ❌ | ✅ |
| Network Config | ❌ | ✅ |
| Monitoring | Basic | Advanced |
| Scalability | Limited | Excellent |

## Recommendation

- **Development/Personal**: Use stdio (simpler)
- **Production/Team**: Use SSE (more features)
- **Enterprise**: Use SSE with auth, SSL, monitoring

See [TRANSPORT_COMPARISON.md](TRANSPORT_COMPARISON.md) for detailed analysis.