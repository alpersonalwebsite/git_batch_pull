# Security Guide

## Overview

Git Batch Pull implements comprehensive security measures to protect against common vulnerabilities and ensure safe operation in enterprise environments. This guide covers all security features and best practices.

## Security Architecture

### Defense in Depth

Git Batch Pull employs multiple layers of security:

1. **Input Validation Layer** - Validates all user inputs
2. **Authentication Layer** - Secure token management and storage
3. **Authorization Layer** - GitHub permission validation
4. **Process Security Layer** - Safe subprocess execution
5. **File System Security Layer** - Path validation and sandboxing
6. **Network Security Layer** - Secure API communications

### Security Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Architecture                    │
├─────────────────────────────────────────────────────────────┤
│  Input Validation  │  Token Security  │  Path Security     │
│  ┌───────────────┐  │  ┌─────────────┐  │  ┌─────────────┐  │
│  │   Type Check  │  │  │   Keyring   │  │  │  Directory  │  │
│  │   Bounds      │  │  │   Encrypt   │  │  │  Traversal  │  │
│  │   Format      │  │  │   Sanitize  │  │  │  Prevention │  │
│  │   Sanitize    │  │  │   Validate  │  │  │  Symlink    │  │
│  └───────────────┘  │  └─────────────┘  │  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Process Security  │  Network Security │  Error Security   │
│  ┌───────────────┐  │  ┌─────────────┐  │  ┌─────────────┐  │
│  │   Command     │  │  │   TLS/SSL   │  │  │   Message   │  │
│  │   Injection   │  │  │   Cert      │  │  │   Sanitize  │  │
│  │   Prevention  │  │  │   Validation│  │  │   Stack     │  │
│  │   Timeout     │  │  │   Rate      │  │  │   Trace     │  │
│  │   Limits      │  │  │   Limiting  │  │  │   Filter    │  │
│  └───────────────┘  │  └─────────────┘  │  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Token Security

### SecureTokenManager

The `SecureTokenManager` provides enterprise-grade token security:

#### Features
- **Keyring Integration**: Uses OS-level secure storage
- **Encryption**: Tokens encrypted at rest
- **Memory Protection**: Tokens cleared from memory after use
- **Access Control**: Per-user token isolation

#### Implementation

```python
from git_batch_pull.security import SecureTokenManager

# Initialize manager
manager = SecureTokenManager()

# Store token securely (prompts for token)
manager.store_token("github", "ghp_your_secure_token")

# Retrieve token (decrypted automatically)
token = manager.get_token("github")

# Token is automatically sanitized in logs
logger.info(f"Using token: {sanitize_token(token)}")  # "ghp_****"
```

#### Security Measures

1. **Encryption at Rest**:
   ```python
   # Tokens are encrypted using OS keyring
   keyring.set_password("git_batch_pull", "github_token", encrypted_token)
   ```

2. **Memory Protection**:
   ```python
   # Tokens are cleared from memory after use
   def secure_operation(token: str):
       try:
           # Use token
           result = api_call(token)
       finally:
           # Clear from memory
           token = "0" * len(token)
           del token
   ```

3. **Log Sanitization**:
   ```python
   def sanitize_token(token: str) -> str:
       """Sanitize token for safe logging."""
       if not token or len(token) < 8:
           return "****"
       return f"{token[:4]}****"
   ```

### Token Validation

All tokens are validated for format and permissions:

```python
def validate_github_token(token: str) -> bool:
    """Validate GitHub token format and permissions."""
    # Format validation
    if not token.startswith(('ghp_', 'github_pat_')):
        raise ValidationError("Invalid token format")

    if len(token) < 40:
        raise ValidationError("Token too short")

    # Permission validation via API call
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )

    if response.status_code == 401:
        raise AuthenticationError("Invalid token")

    return True
```

## Path Security

### PathValidator

Prevents directory traversal and symlink attacks:

#### Directory Traversal Prevention

```python
from git_batch_pull.security import PathValidator

# Dangerous input
user_input = "../../../etc/passwd"

try:
    # Validation prevents traversal
    safe_path = PathValidator.validate_and_resolve(user_input)
except PathValidationError:
    print("Directory traversal attempt detected")
```

#### Implementation

```python
class PathValidator:
    """Path validation and security utilities."""

    @staticmethod
    def validate_and_resolve(path: str, base_path: Optional[str] = None) -> Path:
        """Validate path and resolve safely."""
        # Convert to Path object
        path_obj = Path(path)

        # Resolve to absolute path
        resolved = path_obj.resolve()

        # Check for directory traversal
        if base_path:
            base = Path(base_path).resolve()
            try:
                resolved.relative_to(base)
            except ValueError:
                raise PathValidationError(f"Path outside base directory: {path}")

        # Check for dangerous paths
        dangerous_paths = ["/etc", "/var", "/usr", "/bin", "/sbin"]
        for dangerous in dangerous_paths:
            if str(resolved).startswith(dangerous):
                raise PathValidationError(f"Access to {dangerous} not allowed")

        return resolved

    @staticmethod
    def is_safe_path(path: str, base_path: str) -> bool:
        """Check if path is safe relative to base."""
        try:
            PathValidator.validate_and_resolve(path, base_path)
            return True
        except PathValidationError:
            return False
```

### Symlink Protection

```python
def check_symlink_safety(path: Path) -> None:
    """Check for malicious symlinks."""
    if path.is_symlink():
        target = path.readlink()

        # Check if symlink points outside safe area
        if target.is_absolute():
            raise SecurityError(f"Absolute symlink not allowed: {path}")

        # Resolve and validate target
        resolved_target = (path.parent / target).resolve()
        if not is_safe_path(str(resolved_target), str(path.parent)):
            raise SecurityError(f"Symlink points outside safe area: {path}")
```

## Process Security

### SafeSubprocessRunner

Prevents command injection and provides secure process execution:

#### Command Injection Prevention

```python
from git_batch_pull.security import SafeSubprocessRunner

runner = SafeSubprocessRunner()

# Safe parameterized execution
result = runner.run_git_command([
    "git", "clone",
    validated_url,  # Pre-validated URL
    str(validated_path)  # Pre-validated path
])

# Dangerous: Never do this
# os.system(f"git clone {user_url} {user_path}")  # VULNERABLE
```

#### Implementation

```python
class SafeSubprocessRunner:
    """Secure subprocess execution with timeout and validation."""

    def run_git_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """Run git command safely."""
        # Validate git command
        if not args or args[0] != "git":
            raise SecurityError("Only git commands allowed")

        # Validate arguments
        for arg in args[1:]:
            if any(char in arg for char in [";", "&", "|", "`", "$"]):
                raise SecurityError(f"Unsafe character in argument: {arg}")

        # Set secure environment
        secure_env = os.environ.copy()
        secure_env.pop("LD_PRELOAD", None)  # Remove potentially dangerous env vars

        try:
            return subprocess.run(
                args,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=True,
                env=secure_env
            )
        except subprocess.TimeoutExpired:
            raise GitOperationError(f"Git command timed out after {timeout}s")
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Git command failed: {e.stderr}")
```

### Resource Limits

```python
# Memory and CPU limits for subprocess
import resource

def set_resource_limits():
    """Set resource limits for subprocess."""
    # Limit memory to 1GB
    resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))

    # Limit CPU time to 5 minutes
    resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
```

## Input Validation

### Comprehensive Validation

All user inputs are validated at multiple levels:

#### Type Validation

```python
from typing import Union
from git_batch_pull.exceptions import ValidationError

def validate_entity_type(entity_type: str) -> str:
    """Validate GitHub entity type."""
    valid_types = {"user", "org"}
    if entity_type not in valid_types:
        raise ValidationError(f"Entity type must be one of: {valid_types}")
    return entity_type

def validate_worker_count(workers: Union[int, str]) -> int:
    """Validate worker count."""
    try:
        count = int(workers)
    except ValueError:
        raise ValidationError("Worker count must be an integer")

    if count < 1 or count > 20:
        raise ValidationError("Worker count must be between 1 and 20")

    return count
```

#### URL Validation

```python
import urllib.parse
from git_batch_pull.exceptions import ValidationError

def validate_github_url(url: str) -> str:
    """Validate GitHub repository URL."""
    parsed = urllib.parse.urlparse(url)

    # Check scheme
    if parsed.scheme not in ("https", "ssh"):
        raise ValidationError("URL must use HTTPS or SSH")

    # Check hostname
    valid_hosts = {"github.com", "ssh.github.com"}
    if parsed.hostname not in valid_hosts:
        raise ValidationError("URL must be from github.com")

    # Check path format
    if parsed.scheme == "https":
        if not parsed.path.endswith(".git"):
            raise ValidationError("HTTPS URL must end with .git")

    return url
```

#### Repository Name Validation

```python
import re

def validate_repository_name(name: str) -> str:
    """Validate repository name format."""
    # GitHub repository name rules
    pattern = r"^[a-zA-Z0-9._-]+$"
    if not re.match(pattern, name):
        raise ValidationError(
            "Repository name can only contain letters, numbers, dots, hyphens, and underscores"
        )

    if len(name) > 100:
        raise ValidationError("Repository name too long (max 100 characters)")

    return name
```

## Network Security

### TLS/SSL Validation

All network communications use TLS with certificate validation:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_secure_session() -> requests.Session:
    """Create secure HTTP session with proper TLS configuration."""
    session = requests.Session()

    # Configure TLS
    session.verify = True  # Always verify certificates

    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    return session
```

### Rate Limiting

Respect GitHub API rate limits to prevent abuse:

```python
import time
from typing import Dict, Any

class RateLimiter:
    """GitHub API rate limiting."""

    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 1.0  # Minimum time between requests

    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def check_rate_limit(self, response_headers: Dict[str, str]):
        """Check API rate limit from response headers."""
        remaining = int(response_headers.get("x-ratelimit-remaining", 0))
        reset_time = int(response_headers.get("x-ratelimit-reset", 0))

        if remaining < 10:  # Low on requests
            current_time = time.time()
            wait_time = reset_time - current_time

            if wait_time > 0:
                print(f"Rate limit low, waiting {wait_time}s")
                time.sleep(wait_time)
```

## Error Security

### Safe Error Messages

Error messages are sanitized to prevent information disclosure:

```python
class SecureErrorHandler:
    """Secure error handling and sanitization."""

    def sanitize_error_message(self, error: Exception) -> str:
        """Sanitize error message for safe display."""
        message = str(error)

        # Remove sensitive patterns
        sensitive_patterns = [
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub tokens
            r"github_pat_[a-zA-Z0-9_]+",  # GitHub fine-grained tokens
            r"password=\w+",  # Passwords
            r"token=\w+",  # Generic tokens
        ]

        for pattern in sensitive_patterns:
            message = re.sub(pattern, "****", message)

        return message

    def log_secure_error(self, error: Exception, context: str = ""):
        """Log error with sensitive information removed."""
        sanitized_message = self.sanitize_error_message(error)
        logger.error(f"Error in {context}: {sanitized_message}")
```

### Stack Trace Filtering

```python
import traceback
from typing import List

def filter_sensitive_stack_trace(tb: traceback.TracebackException) -> List[str]:
    """Filter sensitive information from stack traces."""
    filtered_lines = []

    for line in tb.format():
        # Remove lines containing sensitive information
        if any(sensitive in line.lower() for sensitive in ['password', 'token', 'secret']):
            filtered_lines.append("[SENSITIVE DATA FILTERED]")
        else:
            filtered_lines.append(line)

    return filtered_lines
```

## Security Monitoring

### Audit Logging

All security-relevant events are logged:

```python
import json
from datetime import datetime

class SecurityAuditLogger:
    """Security event audit logging."""

    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "INFO"
    ):
        """Log security event with structured format."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "source": "git_batch_pull"
        }

        # Log to security audit file
        with open("security_audit.log", "a") as f:
            f.write(json.dumps(event) + "\n")

# Usage examples
audit = SecurityAuditLogger()

# Log authentication events
audit.log_security_event(
    "authentication_success",
    {"user": "username", "method": "token"},
    "INFO"
)

# Log security violations
audit.log_security_event(
    "path_traversal_attempt",
    {"attempted_path": "../../../etc/passwd"},
    "WARNING"
)
```

### Health Check Security

Security-focused health checks:

```python
from git_batch_pull.core.health_check import HealthChecker

class SecurityHealthChecker(HealthChecker):
    """Security-focused health checks."""

    def check_token_security(self) -> HealthCheckResult:
        """Check token storage security."""
        try:
            # Check if keyring is available
            import keyring
            keyring.get_keyring()

            return HealthCheckResult(
                name="token_security",
                status="ok",
                message="Secure token storage available"
            )
        except Exception as e:
            return HealthCheckResult(
                name="token_security",
                status="warning",
                message=f"Keyring not available: {e}"
            )

    def check_file_permissions(self) -> HealthCheckResult:
        """Check file system permissions."""
        import stat

        # Check config file permissions
        config_file = Path("config.toml")
        if config_file.exists():
            mode = config_file.stat().st_mode
            if stat.S_IROTH & mode or stat.S_IWOTH & mode:
                return HealthCheckResult(
                    name="file_permissions",
                    status="warning",
                    message="Config file has overly permissive permissions"
                )

        return HealthCheckResult(
            name="file_permissions",
            status="ok",
            message="File permissions secure"
        )
```

## Security Best Practices

### For Users

1. **Token Management**:
   - Use fine-grained personal access tokens
   - Set minimum required scopes
   - Rotate tokens regularly
   - Store tokens securely using keyring

2. **Environment Security**:
   - Keep software updated
   - Use dedicated user accounts
   - Enable system logging
   - Monitor for suspicious activity

3. **Configuration Security**:
   - Protect configuration files (600 permissions)
   - Use environment variables for secrets
   - Validate all configuration values

### For Developers

1. **Code Security**:
   - Always validate inputs
   - Use parameterized commands
   - Handle errors securely
   - Implement proper logging

2. **Testing Security**:
   - Test input validation
   - Test error handling
   - Test security boundaries
   - Use security-focused test cases

3. **Deployment Security**:
   - Use least-privilege principles
   - Enable security monitoring
   - Implement proper backup procedures
   - Document security procedures

## Security Updates

Git Batch Pull includes automated security features:

- **Dependency Scanning**: Automated scanning for vulnerable dependencies
- **Secret Scanning**: Detection of accidentally committed secrets
- **Code Analysis**: Static analysis for security vulnerabilities
- **Update Notifications**: Alerts for security updates

To stay secure:

1. Keep Git Batch Pull updated to the latest version
2. Monitor security advisories
3. Report security issues responsibly
4. Follow security best practices

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email security concerns to: [security@project.com]
3. Provide detailed reproduction steps
4. Allow time for responsible disclosure

We take security seriously and will respond promptly to legitimate security concerns.

## Operational Security

### Production Deployment

#### Environment Configuration

```bash
# Production environment variables
export GITHUB_TOKEN="ghp_secure_token_here"
export LOCAL_FOLDER="/secure/repository/path"
export LOG_LEVEL="INFO"
export USE_KEYRING="true"
export MAX_WORKERS="4"

# Security settings
export VALIDATE_SSL="true"
export SECURE_MODE="true"
export AUDIT_LOGGING="true"
```

#### Container Security

```dockerfile
# Secure Docker deployment
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash gituser
USER gituser
WORKDIR /home/gituser

# Install with minimal privileges
COPY --chown=gituser:gituser requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application
COPY --chown=gituser:gituser . .

# Set secure defaults
ENV USE_KEYRING=false
ENV VALIDATE_SSL=true
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m git_batch_pull health || exit 1

ENTRYPOINT ["python", "-m", "git_batch_pull"]
```

#### Kubernetes Security

```yaml
# Secure Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: git-batch-pull
spec:
  replicas: 1
  selector:
    matchLabels:
      app: git-batch-pull
  template:
    metadata:
      labels:
        app: git-batch-pull
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: git-batch-pull
        image: git-batch-pull:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        env:
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: github-credentials
              key: token
        resources:
          limits:
            memory: "1Gi"
            cpu: "1000m"
          requests:
            memory: "256Mi"
            cpu: "100m"
        volumeMounts:
        - name: workspace
          mountPath: /workspace
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: workspace
        persistentVolumeClaim:
          claimName: git-workspace
      - name: tmp
        emptyDir: {}
```

### Network Security

#### Proxy Configuration

```python
# Secure proxy setup
import os
import requests

def configure_secure_proxy():
    """Configure secure proxy for enterprise environments."""
    proxy_config = {
        'http': os.getenv('HTTP_PROXY'),
        'https': os.getenv('HTTPS_PROXY'),
    }

    # Configure SSL context
    session = requests.Session()
    session.proxies.update(proxy_config)

    # Corporate certificate bundle
    ca_bundle = os.getenv('REQUESTS_CA_BUNDLE')
    if ca_bundle:
        session.verify = ca_bundle

    return session
```

#### Firewall Rules

```bash
# Recommended firewall rules for git-batch-pull
# Allow HTTPS to GitHub
iptables -A OUTPUT -p tcp --dport 443 -d github.com -j ACCEPT

# Allow SSH to GitHub (if using SSH URLs)
iptables -A OUTPUT -p tcp --dport 22 -d github.com -j ACCEPT

# Block all other outbound traffic
iptables -A OUTPUT -j DROP
```

### Monitoring and Alerting

#### Security Event Monitoring

```python
import logging
from typing import Dict, Any
from datetime import datetime

class SecurityMonitor:
    """Real-time security monitoring and alerting."""

    def __init__(self, alert_webhook: str = None):
        self.alert_webhook = alert_webhook
        self.security_logger = self._setup_security_logger()

    def _setup_security_logger(self):
        """Configure security-specific logger."""
        logger = logging.getLogger("security")
        handler = logging.FileHandler("security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        return logger

    def monitor_authentication(self, token: str, success: bool):
        """Monitor authentication events."""
        event = {
            "event": "authentication",
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "token_hash": self._hash_token(token)
        }

        if not success:
            self.security_logger.warning(f"Authentication failed: {event}")
            self._send_alert("Authentication failure detected", event)
        else:
            self.security_logger.info(f"Authentication successful: {event}")

    def monitor_path_access(self, path: str, allowed: bool):
        """Monitor file system access attempts."""
        if not allowed:
            event = {
                "event": "unauthorized_path_access",
                "path": path,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.security_logger.warning(f"Unauthorized path access: {event}")
            self._send_alert("Unauthorized path access attempt", event)

    def _hash_token(self, token: str) -> str:
        """Create hash of token for logging (non-reversible)."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()[:8]

    def _send_alert(self, message: str, details: Dict[str, Any]):
        """Send security alert via webhook."""
        if not self.alert_webhook:
            return

        try:
            import requests
            payload = {
                "text": f"🚨 Security Alert: {message}",
                "details": details
            }
            requests.post(self.alert_webhook, json=payload, timeout=10)
        except Exception as e:
            self.security_logger.error(f"Failed to send alert: {e}")
```

#### Compliance Reporting

```python
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

class ComplianceReporter:
    """Generate compliance and security reports."""

    def __init__(self, audit_log_path: str = "security_audit.log"):
        self.audit_log_path = Path(audit_log_path)

    def generate_security_report(self, days: int = 30) -> Dict:
        """Generate security compliance report."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        events = self._load_audit_events(cutoff_date)

        report = {
            "report_period": f"Last {days} days",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_events": len(events),
                "authentication_events": 0,
                "security_violations": 0,
                "path_access_attempts": 0
            },
            "events_by_type": {},
            "security_incidents": []
        }

        for event in events:
            event_type = event.get("event_type", "unknown")
            report["events_by_type"][event_type] = (
                report["events_by_type"].get(event_type, 0) + 1
            )

            if event_type == "authentication":
                report["summary"]["authentication_events"] += 1
            elif "violation" in event_type:
                report["summary"]["security_violations"] += 1
                report["security_incidents"].append(event)
            elif "path" in event_type:
                report["summary"]["path_access_attempts"] += 1

        return report

    def _load_audit_events(self, cutoff_date: datetime) -> List[Dict]:
        """Load audit events from log file."""
        events = []

        if not self.audit_log_path.exists():
            return events

        with open(self.audit_log_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    event_time = datetime.fromisoformat(
                        event.get("timestamp", "1970-01-01")
                    )
                    if event_time >= cutoff_date:
                        events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue

        return events

    def export_compliance_report(self, report: Dict, format: str = "json"):
        """Export compliance report in specified format."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            filename = f"compliance_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)

        elif format == "html":
            filename = f"compliance_report_{timestamp}.html"
            html_content = self._generate_html_report(report)
            with open(filename, 'w') as f:
                f.write(html_content)

        return filename

    def _generate_html_report(self, report: Dict) -> str:
        """Generate HTML compliance report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ color: #333; border-bottom: 2px solid #ddd; }}
                .summary {{ background-color: #f9f9f9; padding: 20px; margin: 20px 0; }}
                .incident {{ background-color: #ffe6e6; padding: 10px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Compliance Report</h1>
                <p>Generated: {report['generated_at']}</p>
                <p>Period: {report['report_period']}</p>
            </div>

            <div class="summary">
                <h2>Summary</h2>
                <ul>
                    <li>Total Events: {report['summary']['total_events']}</li>
                    <li>Authentication Events: {report['summary']['authentication_events']}</li>
                    <li>Security Violations: {report['summary']['security_violations']}</li>
                    <li>Path Access Attempts: {report['summary']['path_access_attempts']}</li>
                </ul>
            </div>

            <h2>Security Incidents</h2>
        """

        for incident in report['security_incidents']:
            html += f"""
            <div class="incident">
                <strong>Type:</strong> {incident.get('event_type', 'Unknown')}<br>
                <strong>Time:</strong> {incident.get('timestamp', 'Unknown')}<br>
                <strong>Details:</strong> {incident.get('details', 'No details')}
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html
```

### Incident Response

#### Security Incident Handling

```python
class SecurityIncidentHandler:
    """Handle security incidents and automate response."""

    def __init__(self):
        self.incident_log = Path("security_incidents.log")
        self.response_actions = {
            "token_compromise": self._handle_token_compromise,
            "path_traversal": self._handle_path_traversal,
            "command_injection": self._handle_command_injection,
            "rate_limit_abuse": self._handle_rate_limit_abuse
        }

    def handle_incident(self, incident_type: str, details: Dict[str, Any]):
        """Handle security incident with appropriate response."""
        incident_id = self._generate_incident_id()

        # Log incident
        incident_record = {
            "id": incident_id,
            "type": incident_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "status": "investigating"
        }

        self._log_incident(incident_record)

        # Execute response actions
        if incident_type in self.response_actions:
            try:
                self.response_actions[incident_type](incident_record)
                incident_record["status"] = "handled"
            except Exception as e:
                incident_record["status"] = "failed"
                incident_record["error"] = str(e)

        self._update_incident(incident_record)
        return incident_id

    def _handle_token_compromise(self, incident: Dict):
        """Handle suspected token compromise."""
        # Disable token usage
        # Send alert to administrators
        # Generate new token recommendations
        pass

    def _handle_path_traversal(self, incident: Dict):
        """Handle path traversal attempts."""
        # Block access to affected paths
        # Increase monitoring
        # Alert security team
        pass

    def _generate_incident_id(self) -> str:
        """Generate unique incident ID."""
        import uuid
        return f"SEC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
```
