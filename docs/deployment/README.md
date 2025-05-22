# Deployment Guide

## Prerequisites
- Kubernetes cluster (v1.29+)
- kubectl configured
- Helm v3
- Docker registry access
- cert-manager installed (for TLS)
- nginx-ingress controller installed

## Configuration

### Environment Variables
Create a `.env` file in the `hermes-ingestor` directory:

```bash
# API Configuration
API_KEY=your-secure-api-key
DEBUG=false
ALLOWED_ORIGINS=https://your-domain.com

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Kubernetes Secrets
Create the required secrets:

```bash
# Create API key secret
kubectl create secret generic hermes-api-key \
  --from-literal=api-key=your-secure-api-key

# Create TLS secret (if not using cert-manager)
kubectl create secret tls hermes-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem
```

## Deployment Steps

1. **Build and Push Docker Images**
   ```bash
   # Build images
   docker build -t your-registry/hermes-ui:latest ./hermes-ui
   docker build -t your-registry/hermes-ingestor:latest ./hermes-ingestor

   # Push images
   docker push your-registry/hermes-ui:latest
   docker push your-registry/hermes-ingestor:latest
   ```

2. **Deploy Qdrant**
   ```bash
   kubectl apply -f hermes-ingestor/k8s/qdrant.yaml
   ```

3. **Deploy Hermes Ingestor**
   ```bash
   kubectl apply -f hermes-ingestor/k8s/deployment.yaml
   ```

4. **Deploy Hermes UI**
   ```bash
   kubectl apply -f hermes-ui/k8s/deployment.yaml
   ```

5. **Apply Network Policies**
   ```bash
   kubectl apply -f hermes-ingestor/k8s/network-policy.yaml
   ```

6. **Deploy Monitoring**
   ```bash
   kubectl apply -f hermes-ingestor/k8s/monitoring.yaml
   ```

## Verification

1. **Check Pod Status**
   ```bash
   kubectl get pods -l app=hermes-ui
   kubectl get pods -l app=hermes-ingestor
   kubectl get pods -l app=qdrant
   ```

2. **Check Services**
   ```bash
   kubectl get svc hermes-ui
   kubectl get svc hermes-ingestor
   kubectl get svc qdrant
   ```

3. **Check Ingress**
   ```bash
   kubectl get ingress hermes-ui-ingress
   ```

4. **Verify TLS**
   ```bash
   curl -v https://your-domain.com/api/health
   ```

## Scaling

The deployment includes a HorizontalPodAutoscaler for automatic scaling:

```bash
kubectl get hpa hermes-ui-hpa
```

Manual scaling:
```bash
kubectl scale deployment hermes-ui --replicas=5
kubectl scale deployment hermes-ingestor --replicas=3
```

## Monitoring

### Prometheus Metrics
The service exposes metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

### Grafana Dashboard
Import the provided dashboard:
```bash
kubectl apply -f hermes-ingestor/k8s/grafana-dashboard.yaml
```

## Backup and Restore

### Qdrant Backup
```bash
# Create backup
kubectl exec -it $(kubectl get pod -l app=qdrant -o jsonpath='{.items[0].metadata.name}') -- \
  qdrant backup /qdrant/storage/backup

# Restore from backup
kubectl exec -it $(kubectl get pod -l app=qdrant -o jsonpath='{.items[0].metadata.name}') -- \
  qdrant restore /qdrant/storage/backup
```

## Troubleshooting

### Common Issues

1. **Pods in CrashLoopBackOff**
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Ingress Issues**
   ```bash
   kubectl describe ingress hermes-ui-ingress
   ```

3. **Network Policy Issues**
   ```bash
   kubectl describe networkpolicy hermes-ingestor-network-policy
   ```

### Logs
```bash
# UI logs
kubectl logs -l app=hermes-ui

# Ingestor logs
kubectl logs -l app=hermes-ingestor

# Qdrant logs
kubectl logs -l app=qdrant
```

## Maintenance

### Updating
1. Build and push new images
2. Update deployment:
   ```bash
   kubectl set image deployment/hermes-ui hermes-ui=your-registry/hermes-ui:new-version
   kubectl set image deployment/hermes-ingestor hermes-ingestor=your-registry/hermes-ingestor:new-version
   ```

### Cleanup
```bash
kubectl delete -f hermes-ui/k8s/deployment.yaml
kubectl delete -f hermes-ingestor/k8s/deployment.yaml
kubectl delete -f hermes-ingestor/k8s/qdrant.yaml
``` 