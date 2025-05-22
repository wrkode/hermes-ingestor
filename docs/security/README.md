# Security Guide

## Overview
This document outlines the security measures implemented in the Hermes Document Ingestion Service and provides guidelines for maintaining and enhancing security.

## Security Features

### Authentication
- API Key authentication for all endpoints
- Secure key storage in Kubernetes secrets
- Key rotation policy
- Rate limiting per API key

### Authorization
- Role-based access control (RBAC)
- Network policies for pod-to-pod communication
- Service account permissions

### Data Protection
- TLS encryption for all communications
- Secure file handling
- Input validation and sanitization
- Output encoding

### Infrastructure Security
- Kubernetes security best practices
- Container security
- Network security
- Resource limits and quotas

## Security Configuration

### API Key Management
1. **Generate Secure Keys**
   ```bash
   # Generate a secure API key
   openssl rand -base64 32
   ```

2. **Store Keys Securely**
   ```bash
   # Create Kubernetes secret
   kubectl create secret generic hermes-api-key \
     --from-literal=api-key=your-secure-key
   ```

3. **Rotate Keys**
   ```bash
   # Update secret
   kubectl create secret generic hermes-api-key \
     --from-literal=api-key=new-secure-key \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

### TLS Configuration
1. **Generate Certificates**
   ```bash
   # Using cert-manager
   kubectl apply -f k8s/certificate.yaml
   ```

2. **Configure Ingress**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
   spec:
     tls:
     - hosts:
       - your-domain.com
       secretName: hermes-tls
   ```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hermes-ingestor-network-policy
spec:
  podSelector:
    matchLabels:
      app: hermes-ingestor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: hermes-ui
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: qdrant
    ports:
    - protocol: TCP
      port: 6333
```

## Security Best Practices

### Code Security
1. **Input Validation**
   ```python
   from pydantic import BaseModel, HttpUrl
   
   class UrlIngestPayload(BaseModel):
       url: HttpUrl  # Validates URL format
       metadata: Optional[Dict[str, Any]]
   ```

2. **File Upload Security**
   ```python
   def validate_file(file: UploadFile):
       # Check file size
       if file.size > settings.max_file_size:
           raise HTTPException(status_code=400, detail="File too large")
       
       # Check file type
       if not file.content_type in settings.allowed_types:
           raise HTTPException(status_code=400, detail="Invalid file type")
   ```

3. **Output Encoding**
   ```python
   from fastapi.responses import HTMLResponse
   
   @app.get("/", response_class=HTMLResponse)
   async def root():
       return HTMLResponse(content=html_content, status_code=200)
   ```

### Container Security
1. **Security Context**
   ```yaml
   securityContext:
     allowPrivilegeEscalation: false
     runAsNonRoot: true
     runAsUser: 1000
     runAsGroup: 1000
     readOnlyRootFilesystem: true
   ```

2. **Resource Limits**
   ```yaml
   resources:
     limits:
       cpu: "1"
       memory: "1Gi"
     requests:
       cpu: "500m"
       memory: "512Mi"
   ```

### Monitoring and Logging
1. **Security Logging**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   logger.warning("Failed login attempt", extra={
       "ip": request.client.host,
       "user": username
   })
   ```

2. **Audit Logging**
   ```python
   def audit_log(action: str, user: str, resource: str):
       logger.info("Audit log", extra={
           "action": action,
           "user": user,
           "resource": resource,
           "timestamp": datetime.utcnow().isoformat()
       })
   ```

## Security Incident Response

### Incident Response Plan
1. **Detection**
   - Monitor logs
   - Review alerts
   - Check system metrics

2. **Containment**
   - Isolate affected systems
   - Block malicious IPs
   - Revoke compromised credentials

3. **Investigation**
   - Collect evidence
   - Analyze logs
   - Determine root cause

4. **Recovery**
   - Restore from backups
   - Apply security patches
   - Update security measures

5. **Post-Incident**
   - Document incident
   - Update procedures
   - Conduct review

### Security Contacts
- Security Team: security@your-domain.com
- Emergency Contact: +1-XXX-XXX-XXXX

## Regular Security Tasks

### Daily Tasks
- Review security logs
- Check for failed login attempts
- Monitor system metrics

### Weekly Tasks
- Review access logs
- Check for suspicious activities
- Update security tools

### Monthly Tasks
- Rotate API keys
- Update dependencies
- Review security policies

### Quarterly Tasks
- Conduct security audit
- Review access controls
- Update security documentation

## Compliance

### Data Protection
- GDPR compliance
- Data retention policies
- Data encryption standards

### Access Control
- Principle of least privilege
- Regular access reviews
- Access logging

### Documentation
- Security policies
- Incident response procedures
- Compliance documentation

## Security Tools

### Recommended Tools
1. **Static Analysis**
   - Bandit (Python)
   - ESLint (JavaScript)
   - SonarQube

2. **Dynamic Analysis**
   - OWASP ZAP
   - Burp Suite
   - Acunetix

3. **Container Security**
   - Trivy
   - Clair
   - Anchore

4. **Kubernetes Security**
   - kube-bench
   - kube-hunter
   - Falco

## Security Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Training
- Security awareness training
- Secure coding practices
- Incident response training

### Updates
- Security bulletins
- Vulnerability databases
- Security patches 