#!/usr/bin/env python3
"""
Script untuk seed/populate Knowledge Base Cards dan Sample Decisions ke database.
Menjalankan: python scripts/seed_kb_and_decisions.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.models import Decision, ThreatLiteAssessment, KBCard
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text


# ============================================================================
# 5 SAMPLE DECISIONS
# ============================================================================

DECISIONS_DATA = [
    {
        "title": "Migrate from Monolith to Microservices Architecture",
        "context": "Current system is a 5-year-old monolithic Rails app. It's becoming hard to scale independently: Payment service needs 10x more capacity than reporting service. Different teams step on each other's toes. Deployment takes 30 mins for entire system. Database is 500GB with mixed concerns.",
        "technical_goal": "Enable independent scaling and deployment of payment, reporting, and admin services. Each service deployable in <5 minutes without affecting others. Target: Support 100K concurrent users (currently 20K).",
        "assumptions": "1. PostgreSQL connection pooling is mature enough for 50+ microservices\n2. gRPC + Protocol Buffers will be faster than REST\n3. Team has capacity to maintain service discovery (Consul/Kubernetes)\n4. Network latency between services <10ms (same data center)\n5. Can migrate incrementally",
        "conscious_simplifications": "1. NOT using full event sourcing (too complex for v1)\n2. NOT implementing CQRS pattern\n3. Synchronous gRPC calls only (no message queues)\n4. Single database per service (no cross-service transactions initially)\n5. No API gateway yet",
        "non_negotiables": "1. MUST maintain backward compatibility with existing REST clients (6 months)\n2. MUST support zero-downtime deployments\n3. MUST have service-to-service authentication (mTLS)\n4. Data consistency: eventual consistency acceptable, max 5-second lag",
        "accepted_worst_case": "1. Service A calls B which calls C → if C fails, cascading failure risk\n2. Network partition → stale data for 5 seconds\n3. Debugging distributed traces harder (need good observability)\n4. Initial 2-3 month slowdown as team learns microservices",
        "status": "active"
    },
    {
        "title": "PostgreSQL + Redis Caching for Persistent State",
        "context": "Microservices creates 3 new services with different query patterns: Payment service (strongly consistent, complex joins), Reporting service (read-heavy, aggregations), Admin service (mostly CRUD, full-text search). Need persistent storage strategy.",
        "technical_goal": "Choose database strategy supporting independent scaling while minimizing operational complexity. Queries respond in <100ms for P95.",
        "assumptions": "1. PostgreSQL JSON support sufficient for semi-structured data\n2. Redis memory cheaper than optimizing PostgreSQL further\n3. Read replicas for reporting (no separate DB)\n4. Full-text search in PostgreSQL sufficient\n5. Team knows PostgreSQL well",
        "conscious_simplifications": "1. NOT using sharding (vertical scaling only until 1TB)\n2. NOT separate OLTP/OLAP (reporting uses read replicas)\n3. NOT DynamoDB for web-scale (PostgreSQL sufficient)\n4. Single Redis instance (no Redis Cluster)\n5. No time-series database (metrics go to Prometheus)",
        "non_negotiables": "1. MUST support ACID transactions within service\n2. MUST have daily automated backups\n3. MUST restore from backup in <1 hour\n4. Data encryption at rest\n5. No vendor lock-in",
        "accepted_worst_case": "1. Redis crashes → cache misses spike 2-3 hours\n2. PostgreSQL CPU maxes → optimize queries or upgrade\n3. Replication lag → reporting data 30-60 seconds behind\n4. Full-text search performance degrades with 1M+ docs",
        "status": "active"
    },
    {
        "title": "OAuth2 + JWT for inter-service auth, SAML for SSO",
        "context": "Microservices need authentication for service-to-service calls. Users need login to admin portal, mobile app, web. Enterprise customers want Okta/Azure AD SSO.",
        "technical_goal": "Implement standard-based auth preventing unauthorized service calls, supporting multiple client types, enabling SSO, auditable.",
        "assumptions": "1. OAuth2 is industry standard\n2. JWT tokens small enough for HTTP headers (<1KB)\n3. JWT secret rotation not needed more than monthly\n4. Can use open-source (Keycloak) or managed service\n5. Refresh tokens can be stored in Redis",
        "conscious_simplifications": "1. NOT implementing API gateway auth\n2. NOT using mTLS yet\n3. Single Keycloak instance\n4. No hardware security module (HSM) for keys\n5. Token rotation every 30 days (manual)",
        "non_negotiables": "1. MUST support logout (token revocation)\n2. MUST have audit log of logins\n3. MUST encrypt passwords (bcrypt/Argon2)\n4. MUST support multi-factor auth\n5. MUST comply with SOC2",
        "accepted_worst_case": "1. Keycloak down → users can't login\n2. JWT secret leaked → need token rotation\n3. Redis down → can't refresh tokens\n4. SAML IdP misconfigured → SSO breaks",
        "status": "active"
    },
    {
        "title": "Prometheus + Loki + Jaeger for observability",
        "context": "Microservices spread across servers need visibility: Which service is slow? Which failed? Resource usage? Debugging requires distributed tracing.",
        "technical_goal": "Implement observability stack: correlate errors across services, search 1M+ logs in <1 sec, show metrics per service, alert on anomalies, support on-call debugging.",
        "assumptions": "1. Open-source stack cheaper than DataDog/New Relic\n2. ELK scales to 1TB/day logs\n3. Developers write structured logs (JSON)\n4. Can afford compute for storage\n5. Jaeger sufficient (not Lightstep)",
        "conscious_simplifications": "1. NOT using APM agents extensively\n2. NOT storing logs forever (30 days hot, 90 archived)\n3. NOT log sampling yet\n4. Single ELK cluster\n5. Grafana dashboards manually created",
        "non_negotiables": "1. MUST support correlation IDs (trace across services)\n2. MUST alert on error rate > 1%\n3. MUST have <5 minute log visibility latency\n4. MUST be queryable by service, environment, user_id\n5. MUST NOT expose PII in logs",
        "accepted_worst_case": "1. Elasticsearch fills up → delete old indices\n2. Jaeger agent crashes → spans lost\n3. Alert threshold misconfigured → false positives\n4. Prometheus scrape fails → missing metrics",
        "status": "active"
    },
    {
        "title": "Kubernetes on AWS EKS for container orchestration",
        "context": "Microservices need auto-scaling, self-healing, rolling updates, service discovery. EC2 with manual scripts error-prone and slow.",
        "technical_goal": "Implement container orchestration: scale independently, deploy in <5 mins, self-heal, abstract server management.",
        "assumptions": "1. Kubernetes learning curve worth it\n2. EKS cheaper than self-managed Kubernetes\n3. Docker containers work for all services\n4. Team can adopt GitOps\n5. Pod resource requests/limits accurately estimated",
        "conscious_simplifications": "1. NOT using advanced Kubernetes features\n2. Single EKS cluster\n3. NOT implementing service mesh (Istio) yet\n4. Basic RBAC\n5. StatefulSets only for databases",
        "non_negotiables": "1. MUST support zero-downtime deployments\n2. MUST auto-scale based on CPU/memory\n3. MUST have health checks (liveness + readiness)\n4. MUST support persistent volumes\n5. MUST rollback in <2 minutes",
        "accepted_worst_case": "1. EKS control plane outage → 30 min no deployments\n2. Pod scheduling fails → manual node scaling\n3. Network policy misconfiguration → services can't reach\n4. PVC deletion accident → data loss",
        "status": "active"
    },
]


# ============================================================================
# 5 THREAT LITE ASSESSMENTS (one per decision)
# ============================================================================

THREAT_ASSESSMENTS_DATA = [
    {
        "decision_idx": 0,
        "context_summary": "Moving from monolith to microservices creates multiple network boundaries. Each service is separate process, increasing attack surface.",
        "assumptions": "1. PostgreSQL connection pooling mature (Exhaustion risk if misconfigured)\n2. gRPC faster than REST (Network latency might not match assumptions)\n3. Service discovery works (Stale registry could route to dead services)\n4. Can migrate incrementally (Data sync between old/new breaks consistency)",
        "assumption_stress_test": "If connection pooling misconfigured: all connections exhausted, services can't query DB. If network latency >10ms: gRPC doesn't provide expected benefit. If discovery fails: services can't find each other.",
        "boundaries_trust": "Now: monolith + single DB. Future: multiple services, gRPC between them, PostgreSQL per service. Risk: service-to-service calls without authentication = service impersonation.",
        "threat_scenarios": "SCENARIO A: Service Impersonation - Attacker spins fake 'Reporting Service' on internal network, intercepts requests, returns malicious data.\nSCENARIO B: Cascading Failure - Reporting Service slow, Payment Service retries exhaust threads, entire system down.\nSCENARIO C: Data Leakage via Logs - Services log errors with sensitive data, logs exposed = data breach.",
        "reflection_outcome": "MITIGATE",
        "reflection_notes": "Service Impersonation REAL & MATERIAL (mTLS fixes). Cascading Failure REAL & MATERIAL (circuit breakers/rate limiting). Logging REAL (PII masking). All mitigatable with known patterns.",
    },
    {
        "decision_idx": 1,
        "context_summary": "PostgreSQL + Redis strategy for distributed data. Multiple services accessing same DB or separate DBs. Replication across instances.",
        "assumptions": "1. PostgreSQL JSON sufficient (Query performance might degrade)\n2. Redis memory cheaper (Memory exhaustion possible)\n3. Read replicas sufficient (Replication lag creates stale data)\n4. Full-text search in PostgreSQL (Performance issues at scale)",
        "assumption_stress_test": "If JSON queries slow: need JSONB indexing or separate DB. If Redis memory exhausts: cache misses spike, DB overloaded. If replication lags: reporting shows old data. If full-text search slow: queries timeout.",
        "boundaries_trust": "Services access shared PostgreSQL + Redis. Risk: unencrypted backup = data exposure. Risk: Redis unencrypted = PII in memory.",
        "threat_scenarios": "SCENARIO A: Backup Exposure - PostgreSQL backup misconfigured (public S3 bucket), attacker downloads 1M user records. SCENARIO B: Cache Poisoning - Attacker compromises app, writes fake data to Redis cache, users see wrong balances. SCENARIO C: Unencrypted Replication - Replication traffic unencrypted, attacker sniffs and steals data.",
        "reflection_outcome": "MITIGATE",
        "reflection_notes": "Backup Exposure CRITICAL (S3 encryption). Cache Poisoning HIGH (cache TTL + integrity checks). Replication Unencrypted HIGH (TLS required). All mitigatable.",
    },
    {
        "decision_idx": 2,
        "context_summary": "OAuth2/JWT + SAML for authentication. JWT stateless (can't revoke until expiration). Secrets stored in env vars.",
        "assumptions": "1. OAuth2 is secure (Implementation matters more)\n2. JWT tokens small (<1KB) (Large tokens exceed headers)\n3. JWT secret rotation monthly safe (Secret compromise needs emergency rotation)\n4. Refresh tokens safe in Redis (Redis breach = persistent access)\n5. SAML configuration correct (Assertion injection possible)",
        "assumption_stress_test": "If JWT secret leaked: all tokens become invalid or attacker can forge. If token revocation missing: user logout = attacker can still use token 30 mins. If refresh token stolen: attacker has persistent access. If SAML validation weak: attacker can impersonate user.",
        "boundaries_trust": "Users authenticate via OAuth2/SAML. Services trust JWT token. Risk: secret compromise = complete auth bypass. Risk: token theft = account takeover.",
        "threat_scenarios": "SCENARIO A: JWT Secret Compromise - Attacker finds secret in deployment config, creates fake admin tokens, withdraws all money. SCENARIO B: Token Revocation Bypass - Attacker steals token, user logs out, attacker still uses token for 30 mins. SCENARIO C: Refresh Token Theft - Attacker breaks into Redis, exfiltrates refresh tokens, accesses accounts indefinitely.",
        "reflection_outcome": "MITIGATE",
        "reflection_notes": "Secret Compromise CRITICAL (Secrets Manager + rotation). Token Revocation REAL (revocation list). Refresh Token Theft REAL (encrypted DB + rotation). All mitigatable with best practices.",
    },
    {
        "decision_idx": 3,
        "context_summary": "Prometheus + Loki + Jaeger for observability. Logs stored in Elasticsearch unencrypted. All services write logs with sensitive data.",
        "assumptions": "1. Open-source cheap (Operational cost high)\n2. ELK scales to 1TB/day (Performance degrades)\n3. Developers write structured logs (Many log sensitive data by mistake)\n4. PII masking automatic (Manual, easy to miss)\n5. Log retention 90 days sufficient (SOC2 requires 7 years)",
        "assumption_stress_test": "If PII in logs: attacker breaks into Elasticsearch, downloads all credit cards. If Elasticsearch unencrypted: compromise = full data leak. If logs retained 90 days: SOC2 audit fails. If retention policy misconfigured: attacker deletes evidence.",
        "boundaries_trust": "Logs are sensitive! They contain request details, user data, errors. Risk: Elasticsearch exposed = breach. Risk: PII in logs = regulatory failure.",
        "threat_scenarios": "SCENARIO A: PII Leakage - Dev logs error: 'Payment failed: card=4111111111111111'. Attacker finds 50K credit cards in logs. SCENARIO B: Elasticsearch Compromise - Attacker finds exposed Elasticsearch, reads all logs = complete visibility of system behavior. SCENARIO C: Log Injection - Attacker sends payload with newlines, injects malicious log entry, frames employee.",
        "reflection_outcome": "MITIGATE",
        "reflection_notes": "PII Leakage CRITICAL & HIGH LIKELIHOOD (masking filter). Elasticsearch Breach CRITICAL (auth + encryption). Log Retention REAL (compliance check). All mitigatable.",
    },
    {
        "decision_idx": 4,
        "context_summary": "Kubernetes orchestration for microservices. Container images pulled from registry. Secrets stored in etcd. RBAC controls access.",
        "assumptions": "1. Kubernetes learning curve worth it (Mistakes common)\n2. EKS cheaper (Total cost ownership high)\n3. Docker containers safe (Vulnerabilities in base images)\n4. GitOps deployment safe (Git repo compromise = cluster compromise)\n5. Pod security policies enforced (Easy to misconfigure)",
        "assumption_stress_test": "If container has CVE: escape to node = cluster compromised. If RBAC permissive: pod accesses secrets it shouldn't. If etcd unencrypted: all secrets leaked. If malicious image deployed: backdoor in all services.",
        "boundaries_trust": "Container = sandbox for code. Kubernetes = orchestration. Risk: container escape = node compromise. Risk: RBAC weak = privilege escalation.",
        "threat_scenarios": "SCENARIO A: Container Escape - Attacker exploits kernel CVE in container, breaks out, accesses Kubernetes tokens = full cluster compromise. SCENARIO B: RBAC Misconfiguration - Payment pod has permission to read all secrets, attacker compromises pod, exfiltrates DB passwords. SCENARIO C: Malicious Image - Attacker compromises CI/CD, pushes malicious image, all pods contain backdoor.",
        "reflection_outcome": "MITIGATE",
        "reflection_notes": "Container Escape CRITICAL (image scanning + pod policies). RBAC Misconfiguration HIGH & COMMON (linting + audit). Malicious Image CRITICAL (image signing + GitOps). All mitigatable.",
    },
]


# ============================================================================
# 30 KB CARDS
# ============================================================================

KB_CARDS_DATA = [
    # ========== MICROSERVICES (6 cards) ==========
    {
        "id": "kb-svc-001",
        "title": "Mutual TLS (mTLS) for Service-to-Service Authentication",
        "tags": ["authentication", "microservices", "encryption", "tls"],
        "category": "Service Security",
        "severity": "HIGH",
        "description": "Implement mTLS to authenticate and encrypt service-to-service communication, preventing impersonation attacks.",
        "content": """## Overview
Mutual TLS ensures both client (Service A) and server (Service B) are authenticated using certificates.

## When to Use
- Service-to-service communication (gRPC, REST over HTTPS)
- Need to prevent service impersonation
- Compliance requirement

## Implementation Approaches
1. **Kubernetes Native:** Use cert-manager + Kubernetes TLS secrets
2. **Service Mesh:** Istio/Linkerd (automatic mTLS)
3. **Manual:** OpenSSL certificate generation

## Deployment Strategy
1. Generate CA certificate (valid 10 years)
2. Generate per-service certificates (valid 90 days)
3. Implement automated rotation
4. Monitor certificate expiration

## Trade-offs
✅ Prevents impersonation, encrypts traffic, auditable
❌ Certificate management overhead, TLS handshake latency""",
        "examples": """### Kubernetes + cert-manager
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: payment-service-cert
spec:
  secretName: payment-tls
  duration: 2160h
  renewBefore: 360h
  commonName: payment.default.svc.cluster.local
  issuerRef:
    name: internal-ca
    kind: Issuer
```

### gRPC + Go
```go
creds, err := credentials.NewServerTLSFromFile(
  "server.crt",
  "server.key",
)
server := grpc.NewServer(grpc.Creds(creds))
```""",
        "source": "OWASP, Kubernetes Documentation, Istio Security",
        "threat_lite_assessment_ids": [1]
    },
    {
        "id": "kb-svc-002",
        "title": "Circuit Breaker Pattern for Preventing Cascading Failures",
        "tags": ["resilience", "microservices", "fault-tolerance", "pattern"],
        "category": "Service Reliability",
        "severity": "HIGH",
        "description": "Implement circuit breaker to stop cascading failures when downstream service fails.",
        "content": """## Problem
When Service A calls Service B which calls Service C, if C fails:
- A keeps retrying B → B overloaded → A also fails
- Entire system goes down

## Solution: Circuit Breaker
Monitor calls. If failure rate exceeds threshold:
1. CLOSED (normal): Requests pass through
2. OPEN (failing): Requests fail fast
3. HALF_OPEN (recovering): Try single request

## Implementation Thresholds
- Failure threshold: > 50% errors in last 100 requests
- Timeout threshold: 5 seconds
- Open → Half-Open: wait 30 seconds

## Benefits
- Prevents cascading failures
- Allows downstream service time to recover
- Fails fast (better UX)
- Automatically recovers""",
        "examples": """### Java: Resilience4j
```java
CircuitBreaker breaker = CircuitBreaker.ofDefaults("reportingService");
Supplier<String> supplier = CircuitBreaker.decorateSupplier(
  breaker,
  () -> reportingServiceClient.getReport(reportId)
);
```""",
        "source": "Sam Newman (Microservices), Resilience4j",
        "threat_lite_assessment_ids": [1]
    },
    {
        "id": "kb-svc-003",
        "title": "Rate Limiting to Prevent Overload and DoS Attacks",
        "tags": ["rate-limiting", "dos-prevention", "api-security"],
        "category": "API Security",
        "severity": "MEDIUM-HIGH",
        "description": "Implement rate limiting to prevent clients from overwhelming services.",
        "content": """## Strategies
1. **Per-Client:** Max 100 req/sec per API key
2. **Global:** Max 10,000 req/sec per service
3. **Endpoint-Specific:** Different limits for endpoints

## Algorithm: Token Bucket
- Bucket holds N tokens
- Each request consumes 1 token
- Tokens refill at rate X per second
- No tokens = request rejected (429)

## Implementation Options
1. API Gateway (Kong, nginx)
2. Service-level middleware
3. Redis-based distributed limiting

## Thresholds
- External APIs: 100 req/sec per client
- Internal calls: 10,000 req/sec
- Burst tolerance: 2x normal for 10 seconds""",
        "examples": """### nginx
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
location /api/ {
  limit_req zone=api_limit burst=20 nodelay;
}
```""",
        "source": "OWASP API Security, Kong Documentation",
        "threat_lite_assessment_ids": [1]
    },
    {
        "id": "kb-svc-004",
        "title": "Bulkhead Pattern for Resource Isolation",
        "tags": ["resilience", "isolation", "thread-pool"],
        "category": "Service Reliability",
        "severity": "MEDIUM",
        "description": "Isolate resources for different service calls to prevent one failure from consuming all resources.",
        "content": """## Problem
If Reporting Service is slow, all threads in Payment Service get stuck.

## Solution: Bulkhead
Allocate separate thread pools:
- Thread pool A (20 threads): Reporting Service calls
- Thread pool B (20 threads): Auth Service calls
- Thread pool C (60 threads): Payment Service logic

If Reporting Service is slow, only pool A exhausted. Pool C handles payments.

## Configuration
- Allocate 20-30% of threads per downstream service
- Monitor utilization (alert at 80%)
- Set thread pool queue size""",
        "examples": """### Java: Hystrix
```java
@HystrixCommand(
  threadPoolKey = "reportingThreadPool",
  threadPoolProperties = {
    @HystrixProperty(name = "coreSize", value = "20")
  }
)
public String getReport() {
  return reportingClient.get();
}
```""",
        "source": "Sam Newman (Microservices), Hystrix Documentation",
        "threat_lite_assessment_ids": [1]
    },
    {
        "id": "kb-svc-005",
        "title": "Service Discovery with Health Checks",
        "tags": ["service-discovery", "kubernetes", "health-checks"],
        "category": "Infrastructure",
        "severity": "MEDIUM",
        "description": "Implement service discovery so services automatically find healthy instances.",
        "content": """## Options
1. **Kubernetes DNS:** Built-in service discovery
2. **Consul:** Advanced with health checks
3. **AWS ECS Service Discovery:** CloudMap

## Health Check Types
1. **Liveness:** Is service alive? (restart if not)
2. **Readiness:** Ready for traffic? (remove from LB if not)
3. **Startup:** Wait for startup (for slow services)

## Thresholds
- Check interval: 10 seconds
- Failure threshold: 3 failed checks = unhealthy
- Success threshold: 1 successful check = healthy""",
        "examples": """### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
```""",
        "source": "Kubernetes Documentation",
        "threat_lite_assessment_ids": [1]
    },
    {
        "id": "kb-svc-006",
        "title": "Request Timeout Configuration",
        "tags": ["resilience", "timeout", "microservices"],
        "category": "API Reliability",
        "severity": "MEDIUM",
        "description": "Set appropriate timeouts to prevent threads from hanging indefinitely.",
        "content": """## Timeout Strategy
1. **Connection Timeout:** 5-10 seconds
2. **Read Timeout:** 10-30 seconds
3. **Request Timeout:** 30-60 seconds

## Rule of Thumb
- P99 latency = baseline
- Set timeout = P99 + 10 seconds

## Cascading Timeouts
If Service A → Service B → Service C:
- C timeout: 10 seconds
- B timeout: 20 seconds (> C)
- A timeout: 30 seconds (> B)

Prevents all layers timing out simultaneously.""",
        "examples": """### Java: RestTemplate
```java
factory.setConnectTimeout(5000);
factory.setReadTimeout(30000);
```""",
        "source": "Microservices Best Practices",
        "threat_lite_assessment_ids": [1]
    },
    
    # ========== DATABASE (7 cards) ==========
    {
        "id": "kb-db-001",
        "title": "PostgreSQL Connection Pooling with PgBouncer",
        "tags": ["database", "connection-pool", "postgresql"],
        "category": "Database",
        "severity": "HIGH",
        "description": "Use PgBouncer to prevent connection pool exhaustion.",
        "content": """## Problem
50 microservices × 20 connections = 1000 connections → exhausts PostgreSQL (default 200)

## Solution: Connection Pooler (PgBouncer)
PgBouncer sits between services and PostgreSQL:
- Services connect to PgBouncer
- PgBouncer maintains fewer connections to PostgreSQL
- Multiplexing: reuse connections

## Configuration
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25

## Benefits
- Services don't exhaust database connections
- Multiplexing reduces database load
- Connection reuse is fast""",
        "examples": """### Docker Compose Setup
```yaml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    DATABASES_HOST: postgres
    PGBOUNCER_POOL_MODE: transaction
    PGBOUNCER_MAX_CLIENT_CONN: 1000
    PGBOUNCER_DEFAULT_POOL_SIZE: 25
```""",
        "source": "PgBouncer Documentation, PostgreSQL Best Practices",
        "threat_lite_assessment_ids": [2]
    },
    {
        "id": "kb-db-002",
        "title": "Parameterized Queries to Prevent SQL Injection",
        "tags": ["database-security", "sql-injection"],
        "category": "Database Security",
        "severity": "CRITICAL",
        "description": "Use parameterized queries to prevent SQL injection attacks.",
        "content": """## Problem
Concatenating SQL with user input:
```sql
query = "SELECT * FROM users WHERE email = '" + user_email + "'"
// User input: admin' OR '1'='1
// Result: SELECT ALL USERS
```

## Solution: Parameterized Queries
```sql
query = "SELECT * FROM users WHERE email = ?"
execute(query, [user_email])
```
Database driver treats user input as literal string, not code.

## Best Practice
- ALWAYS use parameterized queries
- Never concatenate user input into SQL
- Use ORM (Hibernate, SQLAlchemy)""",
        "examples": """### Java: PreparedStatement
```java
PreparedStatement stmt = connection.prepareStatement(
  "SELECT * FROM users WHERE email = ?"
);
stmt.setString(1, user_email);
ResultSet rs = stmt.executeQuery();
```""",
        "source": "OWASP SQL Injection, CWE-89",
        "threat_lite_assessment_ids": [2]
    },
    {
        "id": "kb-db-003",
        "title": "Encrypted Database Backups with Regular Testing",
        "tags": ["backup", "encryption", "disaster-recovery"],
        "category": "Database",
        "severity": "CRITICAL",
        "description": "Encrypt database backups and test restore regularly.",
        "content": """## Backup Strategy
1. **Frequency:** Daily automated backups
2. **Retention:** 90 days hot, archive to Glacier
3. **Encryption:** AES-256 at rest
4. **Location:** Separate storage system

## Restore Testing
- Monthly: Restore to test environment
- Verify data integrity
- Measure restore time (should be < 1 hour)

## Compliance
- HIPAA: 7 year retention
- SOC2: Encrypted + tested backups
- GDPR: Support data deletion

## Access Control
- Only DBA team can download
- Audit logging: who accessed when
- Encryption key in HSM""",
        "examples": """### AWS RDS: Automated Backups
```json
{
  "DBInstanceIdentifier": "production-db",
  "BackupRetentionPeriod": 90,
  "StorageEncrypted": true,
  "KmsKeyId": "arn:aws:kms:..."
}
```""",
        "source": "AWS RDS, PostgreSQL Documentation",
        "threat_lite_assessment_ids": [2]
    },
    {
        "id": "kb-db-004",
        "title": "Redis Cache Security with TTL and Memory Limits",
        "tags": ["caching", "redis", "security"],
        "category": "Caching",
        "severity": "MEDIUM-HIGH",
        "description": "Secure Redis with authentication, encryption, memory limits, and TTL.",
        "content": """## Security Layers
1. **Authentication:** Redis ACL or requirepass
2. **Encryption:** TLS for network traffic
3. **Memory:** Eviction policies + limits
4. **TTL:** Automatic key expiration

## Configuration
requirepass strong_password
maxmemory 64gb
maxmemory-policy allkeys-lru
tls-port 6379

## Application-Level TTL
SET user:123:cache value EX 3600  # 1 hour

## Memory Alerts
- Alert at 80% utilization
- Scale up if consistent high usage
- Monitor eviction rate""",
        "examples": """### Redis ACL
```redis
ACL SETUSER payment-service on >password ~payment:* +get +set
```""",
        "source": "Redis Documentation",
        "threat_lite_assessment_ids": [2]
    },
    {
        "id": "kb-db-005",
        "title": "PostgreSQL Read Replicas for Scaling Reads",
        "tags": ["database", "scaling", "read-replica"],
        "category": "Database",
        "severity": "MEDIUM",
        "description": "Use read replicas to offload read-heavy queries from primary.",
        "content": """## Architecture
Primary (writes) → Replication → Replica 1 (reads)
                                ├─ Replica 2 (reads)
                                └─ Replica 3 (reads)

## Data Flow
- Writes to Primary only
- Reads from Replicas (distributed)
- Replication lag: 30-60 seconds

## Configuration
1. Create replica from primary
2. Configure: wal_level = replica, max_wal_senders = 10
3. Connection string for reads: point to replica

## Failover
If Primary fails:
1. Promote Replica 1 to new Primary
2. Update connection strings""",
        "examples": """### AWS RDS: Create Read Replica
```bash
aws rds create-db-instance-read-replica \\
  --db-instance-identifier production-replica-1 \\
  --source-db-instance-identifier production-primary
```""",
        "source": "PostgreSQL Documentation, AWS RDS",
        "threat_lite_assessment_ids": [2]
    },
    {
        "id": "kb-db-006",
        "title": "Encrypted PostgreSQL Connections with TLS",
        "tags": ["database-security", "encryption", "postgresql"],
        "category": "Database Security",
        "severity": "HIGH",
        "description": "Enforce TLS/SSL encryption for all PostgreSQL connections.",
        "content": """## Configuration
On PostgreSQL server:
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'

Connection requirement:
hostssl all all 0.0.0.0/0 md5
# Force SSL for all connections

## Client Certificate (optional)
- Server certificate: authenticates DB to clients
- Client certificate: authenticates client to DB
- Prevents unauthorized clients from connecting

## Verification
Check connection is encrypted with TLS""",
        "examples": """### PostgreSQL Server Setup
```bash
openssl req -x509 -days 365 -nodes -newkey rsa:2048 \\
  -keyout /etc/postgresql/server.key \\
  -out /etc/postgresql/server.crt
```""",
        "source": "PostgreSQL SSL Documentation",
        "threat_lite_assessment_ids": [2]
    },

    # ========== AUTHENTICATION (8 cards) ==========
    {
        "id": "kb-auth-001",
        "title": "JWT Secret Management using Cloud Secrets Manager",
        "tags": ["authentication", "secrets-management", "jwt"],
        "category": "Authentication",
        "severity": "CRITICAL",
        "description": "Store JWT secrets in managed secret store with automatic rotation.",
        "content": """## Problem
Storing JWT secret in env vars:
- Visible in Docker history
- Logged in CI/CD systems
- Exposed if deployment config leaked

## Solution: Secrets Manager
AWS Secrets Manager / HashiCorp Vault:
- Encrypt secrets at rest
- Audit access (who read when)
- Automatic rotation (every 7-30 days)
- Revoke old secret versions

## Secret Rotation Strategy
1. Generate new secret
2. Support both old + new secrets (validation period)
3. After validation, old secret is invalid
4. Force token refresh

## Automation
- Lambda function rotates automatically
- Application reloads secret (no restart)""",
        "examples": """### AWS Secrets Manager
```bash
aws secretsmanager create-secret \\
  --name prod/jwt-secret \\
  --secret-string "$(openssl rand -base64 32)"
```""",
        "source": "AWS Secrets Manager, 12 Factor App",
        "threat_lite_assessment_ids": [3]
    },
    {
        "id": "kb-auth-002",
        "title": "Token Revocation List for Immediate Logout",
        "tags": ["authentication", "jwt", "revocation"],
        "category": "Authentication",
        "severity": "HIGH",
        "description": "Implement token revocation list to prevent use of tokens after logout.",
        "content": """## Problem
JWT stateless - can't invalidate until expiration (30 mins):
- User logs out at 10:00 AM
- Attacker steals token at 10:05 AM
- Attacker can use token until 10:30 AM (20 mins of fraud)

## Solution: Revocation List
Maintain blacklist of revoked tokens:
1. On logout: add token to revocation list
2. On request: check if token in revocation list
3. If yes: reject request
4. TTL = token expiration (auto-cleanup)

## Implementation
- Store in Redis (fast, memory efficient)
- Key: token_id, Value: true
- Cost: ~1KB per token

## Trade-off
✅ Immediate logout, prevents fraud
❌ Adds latency (Redis lookup)""",
        "examples": """### Redis Revocation
```python
def logout_user(token):
  redis.setex(f"token_blacklist:{token}", 1800, "true")

def is_token_revoked(token):
  return redis.exists(f"token_blacklist:{token}")
```""",
        "source": "Auth0, JWT Best Practices",
        "threat_lite_assessment_ids": [3]
    },
    {
        "id": "kb-auth-003",
        "title": "SAML Assertion Validation for Enterprise SSO",
        "tags": ["authentication", "saml", "sso"],
        "category": "Authentication",
        "severity": "CRITICAL",
        "description": "Properly validate SAML assertions to prevent authentication bypass.",
        "content": """## SAML Assertion Validation Checklist
1. **Signature Verification:** Validate SAML signature using IdP's public cert
2. **Issuer Validation:** Verify <Issuer> matches expected IdP URL
3. **Assertion Consumer URL:** Verify matches your endpoint
4. **Audience Validation:** Verify matches service entity ID
5. **Not Before / Not On Or After:** Verify assertion hasn't expired
6. **Signature Algorithm:** Reject weak algorithms, require RSA-SHA256+
7. **XML Schema Validation:** Validate SAML XML structure

## Implementation
Use well-tested libraries (Keycloak, OpenSAML) not custom parsing.""",
        "examples": """### Keycloak SAML Validation (built-in)
Keycloak automatically validates all aspects.
Just configure in UI.""",
        "source": "OWASP SAML Security, Okta Documentation",
        "threat_lite_assessment_ids": [3]
    },
    {
        "id": "kb-auth-004",
        "title": "Refresh Token Rotation for Long-Lived Sessions",
        "tags": ["authentication", "oauth2", "refresh-token"],
        "category": "Authentication",
        "severity": "HIGH",
        "description": "Implement refresh token rotation to limit exposure if token is stolen.",
        "content": """## Problem
If refresh token stolen:
- Attacker can get new access tokens indefinitely
- User has no way to revoke old refresh token
- Attacker has persistent access

## Solution: Rotation
Each time refresh token is used:
1. Issue new access token
2. Issue new refresh token
3. Invalidate old refresh token
4. Attacker's old token becomes useless

## Token Family
- Detect if token used twice (indicates theft)
- Revoke entire family (force re-login)""",
        "examples": """### OAuth2 Refresh Token Rotation
POST /oauth/token
grant_type=refresh_token&
refresh_token=refresh_token_A

RESPONSE:
{
  "access_token": "new_access_token",
  "refresh_token": "refresh_token_B"
}

# Old refresh_token_A now invalid
```""",
        "source": "OAuth2 Security Best Practices, Auth0",
        "threat_lite_assessment_ids": [3]
    },
    {
        "id": "kb-auth-005",
        "title": "Multi-Factor Authentication (MFA) Implementation",
        "tags": ["authentication", "mfa", "2fa"],
        "category": "Authentication",
        "severity": "MEDIUM-HIGH",
        "description": "Implement MFA to prevent account takeover via password compromise.",
        "content": """## MFA Methods
1. **TOTP:** Google Authenticator, Authy (6-digit code every 30 sec)
2. **SMS/Email OTP:** Server sends code
3. **Hardware Keys:** YubiKey, Google Titan (most secure)

## Implementation Strategy
1. **Optional for users:** Let users enable MFA
2. **Required for admins:** Mandatory for admin accounts
3. **Backup codes:** Allow login if MFA device lost

## SOC2 Compliance
Usually requires MFA for admin/sensitive access.""",
        "examples": """### TOTP (Node.js)
```javascript
const speakeasy = require('speakeasy');
const secret = speakeasy.generateSecret();
const verified = speakeasy.totp.verify({
  secret: secret,
  token: user_input,
  window: 2
});
```""",
        "source": "OWASP, Speakeasy Library, NIST Guidelines",
        "threat_lite_assessment_ids": [3]
    },
    {
        "id": "kb-auth-006",
        "title": "OAuth2 Authorization Code Flow for Secure Delegation",
        "tags": ["authentication", "oauth2", "authorization"],
        "category": "Authentication",
        "severity": "MEDIUM",
        "description": "Implement OAuth2 authorization code flow for delegated access.",
        "content": """## Why OAuth2?
Users don't share password with third-party apps.

## Authorization Code Flow
1. User clicks "Login with Google"
2. Redirected to Google login
3. User logs in (Google, not your app)
4. Google redirects: myapp.com/callback?code=AUTH_CODE
5. Your backend exchanges code for token
6. Your app logged in as user@gmail.com

## Security Features
- User password never shared
- Code short-lived (10 minutes)
- Code one-time use
- Token can be revoked
- Works across devices""",
        "examples": """### Node.js with Passport.js
```javascript
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: 'http://localhost:3000/auth/google/callback'
}));
```""",
        "source": "OAuth2 RFC 6749, Google OAuth2 Docs",
        "threat_lite_assessment_ids": [3]
    },

    # ========== OBSERVABILITY (6 cards) ==========
    {
        "id": "kb-obs-001",
        "title": "PII Masking in Logs",
        "tags": ["logging", "pii-masking", "privacy", "gdpr"],
        "category": "Logging",
        "severity": "CRITICAL",
        "description": "Mask PII in logs to prevent data exposure.",
        "content": """## PII Categories to Mask
1. **Payment Data:** Credit card numbers, CVV
2. **Personal Info:** Email, phone, SSN
3. **Credentials:** Passwords, API keys, tokens
4. **Medical:** Health records
5. **Location:** Home address

## Masking Patterns
Credit card: 4111-1111-1111-1111 → 4111-****-****-1111
Email: user@example.com → u***@example.com
Phone: 555-123-4567 → 555-****567

## Implementation Options
1. Application-level: Filter in code
2. Logging framework: Filter in Logback/Log4j
3. Log shipper: Filter in Filebeat
4. ELK: Filter in Elasticsearch""",
        "examples": """### Java: Logback Filter
```java
public class PIIFilter extends Filter<ILoggingEvent> {
  @Override
  public FilterReply decide(ILoggingEvent event) {
    String message = event.getFormattedMessage();
    message = message.replaceAll(
      "\\\\b\\\\d{4}-?\\\\d{4}-?\\\\d{4}-?\\\\d{4}\\\\b",
      "****-****-****-****"
    );
    return FilterReply.ACCEPT;
  }
}
```""",
        "source": "GDPR, HIPAA, PCI-DSS Compliance",
        "threat_lite_assessment_ids": [4]
    },
    {
        "id": "kb-obs-002",
        "title": "Elasticsearch Security and Access Control",
        "tags": ["elasticsearch", "security", "authentication"],
        "category": "Logging Infrastructure",
        "severity": "CRITICAL",
        "description": "Secure Elasticsearch with authentication, encryption, and RBAC.",
        "content": """## Security Layers
1. **Network:** Not exposed to internet
2. **Authentication:** Username/password required
3. **Encryption:** TLS for network traffic
4. **Authorization:** RBAC (who accesses what)
5. **Audit:** Track all access

## Configuration
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.http.ssl.enabled: true

## RBAC Setup
- Ops team: all logs
- Backend team: backend logs only
- Security team: threat queries

## Monitoring
- Alert on failed auth attempts
- Alert on unusual queries
- Audit trail of all access""",
        "examples": """### Create User Role
```bash
curl -X POST "http://localhost:9200/_security/role/backend_viewer" \\
  -u elastic:password \\
  -H "Content-Type: application/json" \\
  -d'{
    "indices": [{
      "names": ["logs-backend-*"],
      "privileges": ["read"]
    }]
  }'
```""",
        "source": "Elasticsearch Security, NIST Cybersecurity Framework",
        "threat_lite_assessment_ids": [4]
    },
    {
        "id": "kb-obs-003",
        "title": "Log Retention Policy and Cold Storage Archival",
        "tags": ["logging", "retention", "archival", "compliance"],
        "category": "Logging",
        "severity": "MEDIUM-HIGH",
        "description": "Define log retention and archive to cold storage for cost savings.",
        "content": """## Retention Strategy
- **Hot (30 days):** Elasticsearch (searchable)
- **Warm (60 days):** AWS S3 Standard
- **Cold (365+ days):** AWS S3 Glacier

## Cost Calculation
- Elasticsearch: $0.10/GB/month
- S3 Standard: $0.023/GB/month
- S3 Glacier: $0.004/GB/month

## Compliance Requirements
- HIPAA: 7 years
- SOC2: 1-2 years
- GDPR: 30 days (delete after right-to-be-forgotten)
- PCI-DSS: 1 year

## Immutable Archives
- Enable S3 Object Lock
- Prevents deletion
- Required for forensics""",
        "examples": """### S3 Lifecycle Configuration
```xml
<Transitions>
  <Transition>
    <Days>30</Days>
    <StorageClass>STANDARD_IA</StorageClass>
  </Transition>
  <Transition>
    <Days>90</Days>
    <StorageClass>GLACIER</StorageClass>
  </Transition>
</Transitions>
```""",
        "source": "AWS S3, ELK Lifecycle, Compliance Requirements",
        "threat_lite_assessment_ids": [4]
    },
    {
        "id": "kb-obs-004",
        "title": "Structured Logging for Better Searchability",
        "tags": ["logging", "structured-logging", "json"],
        "category": "Logging",
        "severity": "MEDIUM",
        "description": "Use structured logging (JSON) for powerful querying.",
        "content": """## Why Structured Logging?
**Unstructured:**
2026-02-07 ERROR Payment failed for user 123
Hard to query by user_id

**Structured (JSON):**
{
  "timestamp": "2026-02-07T10:30:45Z",
  "level": "ERROR",
  "service": "payment",
  "user_id": "123",
  "action": "payment_failed"
}
Easy to parse, search by fields

## Fields to Include
1. timestamp, level, message
2. trace_id (correlate across services)
3. span_id (correlate within service)
4. service_name, environment
5. user_id, request_id""",
        "examples": """### Node.js: Winston Logger
```javascript
const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new winston.transports.Console()
  ]
});

logger.info('payment_processed', {
  user_id: 123,
  amount: 100,
  trace_id: req.id
});
```""",
        "source": "ELK Best Practices, OpenTelemetry",
        "threat_lite_assessment_ids": [4]
    },
    {
        "id": "kb-obs-005",
        "title": "Distributed Tracing with Jaeger",
        "tags": ["tracing", "jaeger", "observability"],
        "category": "Observability",
        "severity": "MEDIUM",
        "description": "Implement distributed tracing to follow requests across services.",
        "content": """## Problem
Request: Frontend → Payment API → Reporting API → Database
If something fails, which service? Hard to debug without tracing.

## Solution: Distributed Tracing
Assign trace_id to request, track through all services.

## Implementation
1. Generate trace_id on entry
2. Pass trace_id in HTTP headers
3. Log trace_id with every log
4. Send spans to Jaeger collector
5. View traces in Jaeger UI""",
        "examples": """### Node.js: Jaeger Client
```javascript
const tracer = initTracer(config);

app.use((req, res, next) => {
  const wireCtx = tracer.extract(
    opentracing.Format.HTTP_HEADERS,
    req.headers
  );
  const span = tracer.startSpan('http_request', { childOf: wireCtx });
  req.span = span;
  next();
});
```""",
        "source": "OpenTelemetry, Jaeger Documentation",
        "threat_lite_assessment_ids": [4]
    },
    {
        "id": "kb-obs-006",
        "title": "Prometheus Metrics & Alerting",
        "tags": ["monitoring", "prometheus", "alerting"],
        "category": "Observability",
        "severity": "MEDIUM",
        "description": "Collect metrics and set up alerts on anomalies.",
        "content": """## Key Metrics (RED)
- Rate: requests per second
- Errors: error rate %
- Duration: latency (P50, P95, P99)

## Alert Thresholds
- Error rate > 1% → page on-call
- P99 latency > 500ms → warning
- CPU > 80% → scale up
- Memory > 85% → scale up

## Best Practices
- Use business metrics (payments/sec, revenue/hour)
- Correlate with user impact
- Alert on trends, not just absolute values""",
        "examples": """### Prometheus Alert Rules
```yaml
- alert: HighErrorRate
  expr: rate(payments_failure[5m]) > 0.01
  for: 5m
  annotations:
    summary: "Payment error rate > 1%"
```""",
        "source": "Prometheus Docs, Grafana Best Practices",
        "threat_lite_assessment_ids": [4]
    },

    # ========== KUBERNETES (6 cards) ==========
    {
        "id": "kb-k8s-001",
        "title": "Container Image Vulnerability Scanning",
        "tags": ["kubernetes", "container-security", "image-scanning"],
        "category": "Container Security",
        "severity": "CRITICAL",
        "description": "Scan container images for known vulnerabilities before deployment.",
        "content": """## Scanning Tools
1. **Trivy** (open-source, fast)
2. **Anchore** (detailed)
3. **AWS ECR Scanning** (integrated)
4. **Snyk** (DevSecOps)

## Workflow
1. Build Docker image
2. Scan for vulnerabilities
3. Block if CRITICAL CVE
4. Fix (update base image)
5. Rebuild and rescan

## Policy
- Block: CRITICAL severity CVE
- Warn: HIGH severity CVE
- Allow: LOW/MEDIUM (review)

## Continuous Scanning
- Scan weekly (new CVEs discovered)
- Alert if new CVE in deployed image""",
        "examples": """### Trivy CLI
```bash
trivy image my-app:1.0.0
trivy image --exit-code 1 --severity CRITICAL my-app:1.0.0
trivy image --format json my-app:1.0.0 > scan-results.json
```""",
        "source": "Trivy, OWASP, NIST Cybersecurity",
        "threat_lite_assessment_ids": [5]
    },
    {
        "id": "kb-k8s-002",
        "title": "Kubernetes Pod Security Policies",
        "tags": ["kubernetes", "pod-security", "security-policy"],
        "category": "Kubernetes Security",
        "severity": "HIGH",
        "description": "Use Pod Security Policies to restrict container privileges.",
        "content": """## Security Restrictions
1. **No root:** Containers run as non-root user
2. **No privileged:** No privilege escalation
3. **Read-only filesystem:** Container immutable
4. **Network policies:** Restrict pod-to-pod traffic
5. **No host networking:** Pod can't use host network

## Migration Path
- K8s < 1.25: Pod Security Policies
- K8s >= 1.25: Pod Security Standards

## Policy Levels
- **Restricted:** Highest security
- **Baseline:** Minimal restrictions
- **Privileged:** Unrestricted (system pods only)""",
        "examples": """### Pod Security Standard (K8s >= 1.25)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    pod-security.kubernetes.io/enforce: restricted
```""",
        "source": "Kubernetes Pod Security, NIST Guidelines",
        "threat_lite_assessment_ids": [5]
    },
    {
        "id": "kb-k8s-003",
        "title": "Kubernetes RBAC (Role-Based Access Control)",
        "tags": ["kubernetes", "rbac", "access-control"],
        "category": "Kubernetes Security",
        "severity": "HIGH",
        "description": "Implement RBAC to ensure minimum required permissions.",
        "content": """## RBAC Components
1. **ServiceAccount:** Identity for a pod
2. **Role:** Set of permissions
3. **RoleBinding:** Grant role to account

## Permission Types
- **get, list, watch:** Read operations
- **create, update, patch:** Modify
- **delete:** Delete

## Principle of Least Privilege
Each service only has needed permissions.

## Danger Signs
verbs: ["*"] → Do anything
resources: ["*"] → On any resource
apiGroups: ["*"] → All API groups""",
        "examples": """### Restrictive Service Account
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: payment-service-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["payment-db-secret"]
  verbs: ["get"]
```""",
        "source": "Kubernetes RBAC Docs, NIST Guidelines",
        "threat_lite_assessment_ids": [5]
    },
    {
        "id": "kb-k8s-004",
        "title": "Kubernetes Network Policies",
        "tags": ["kubernetes", "network-policy", "segmentation"],
        "category": "Kubernetes Networking",
        "severity": "MEDIUM-HIGH",
        "description": "Use Network Policies for zero-trust pod networking.",
        "content": """## Default Behavior
Without policies: All pods talk to all pods.

## With Policies
Deny all, then explicitly allow needed traffic.

## Policy Types
1. **Ingress:** Who can reach my pod
2. **Egress:** Who my pod can reach

## Example
Payment pod receives from:
- API Gateway (ingress)
- Load Balancer (ingress)

Payment pod sends to:
- PostgreSQL (egress)
- Redis (egress)
- Logging service (egress)""",
        "examples": """### Default Deny All
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: payment
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```""",
        "source": "Kubernetes Network Policies, NIST Zero Trust",
        "threat_lite_assessment_ids": [5]
    },
    {
        "id": "kb-k8s-005",
        "title": "Kubernetes Secrets Encryption at Rest",
        "tags": ["kubernetes", "secrets", "encryption"],
        "category": "Kubernetes Security",
        "severity": "CRITICAL",
        "description": "Encrypt Kubernetes secrets at rest in etcd.",
        "content": """## Problem
By default, secrets stored in etcd unencrypted:
- If etcd accessed, all secrets exposed
- Database passwords, API keys readable

## Solution: Encryption at Rest
1. Generate encryption key
2. Configure KMS provider
3. Restart API server
4. New secrets encrypted

## AWS KMS Integration
- Store key in AWS KMS (HSM)
- Kubernetes API server calls KMS
- Key never stored on disk
- Audit: CloudTrail logs access""",
        "examples": """### AWS EKS: Enable Encryption
```bash
aws kms create-key \\
  --description "EKS secret encryption key"

aws eks create-cluster \\
  --name my-cluster \\
  --encryption-config resources=secrets,provider="{keyArn=$KEY_ARN}"
```""",
        "source": "Kubernetes Encryption at Rest, AWS EKS",
        "threat_lite_assessment_ids": [5]
    },
    {
        "id": "kb-k8s-006",
        "title": "Kubernetes Audit Logging",
        "tags": ["kubernetes", "audit-logging", "compliance"],
        "category": "Kubernetes Security",
        "severity": "MEDIUM-HIGH",
        "description": "Enable audit logging to track all API calls.",
        "content": """## Audit Log Contents
- Who (user/service account)
- What (create, delete, update)
- When (timestamp)
- Where (pod, namespace)
- Why (reason, status)

## Audit Levels
- **None:** Don't log
- **Metadata:** User, resource, action
- **RequestResponse:** Also request/response body

## Policy
- Log CRITICAL: denied requests, secret access, RBAC changes
- Log METADATA: most other operations

## Monitoring
- Alert on failed auth attempts
- Alert on unusual queries
- Audit trail of all access""",
        "examples": """### Enable Audit Logging
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log secret access
  - level: RequestResponse
    verbs: ["get", "create"]
    resources:
      - group: ""
        resources: ["secrets"]
  
  # Log RBAC changes
  - level: RequestResponse
    apiGroups: ["rbac.authorization.k8s.io"]
    verbs: ["create", "update", "patch"]
  
  # Default
  - level: Metadata
```""",
        "source": "Kubernetes Audit Logging, NIST Cybersecurity",
        "threat_lite_assessment_ids": [5]
    },
]


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to seed all data."""
    
    print("\n" + "="*80)
    print("🚀 DECISIONS + THREAT LITE + KB CARDS SEEDER")
    print("="*80 + "\n")
    
    # Connect to database
    print("📊 Connecting to database...")
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1
    
    # ========== SEED DECISIONS ==========
    print("📋 SEEDING 5 SAMPLE DECISIONS")
    print("-" * 80)
    
    inserted_decisions = 0
    for idx, decision_data in enumerate(DECISIONS_DATA, 1):
        try:
            existing = db.query(Decision).filter(
                Decision.title == decision_data['title']
            ).first()
            
            if existing:
                print(f"⏭️  [{idx}] Skipping: {decision_data['title'][:60]}")
                continue
            
            decision = Decision(**decision_data, created_at=datetime.now(), updated_at=datetime.now())
            db.add(decision)
            db.flush()  # Get the ID before commit
            
            print(f"✅ [{idx}] Created: {decision_data['title'][:60]}")
            inserted_decisions += 1
            
        except Exception as e:
            db.rollback()
            print(f"❌ [{idx}] Error: {str(e)[:50]}")
    
    db.commit()
    print(f"\n✅ Decisions seeded: {inserted_decisions}\n")
    
    # ========== SEED THREAT LITE ASSESSMENTS ==========
    print("⚠️  SEEDING 5 THREAT LITE ASSESSMENTS")
    print("-" * 80)
    
    inserted_assessments = 0
    decisions_list = db.query(Decision).all()
    
    for idx, assessment_data in enumerate(THREAT_ASSESSMENTS_DATA, 1):
        try:
            decision_idx = assessment_data.pop("decision_idx")
            if decision_idx >= len(decisions_list):
                print(f"⏭️  [{idx}] Skipping: Decision index {decision_idx} not found")
                continue
            
            assessment_data['decision_id'] = decisions_list[decision_idx].id
            assessment_data['created_at'] = datetime.now()
            assessment_data['updated_at'] = datetime.now()
            
            assessment = ThreatLiteAssessment(**assessment_data)
            db.add(assessment)
            
            print(f"✅ [{idx}] Created Threat Assessment for Decision {decision_idx + 1}")
            inserted_assessments += 1
            
        except Exception as e:
            db.rollback()
            print(f"❌ [{idx}] Error: {str(e)[:50]}")
    
    db.commit()
    print(f"\n✅ Threat Assessments seeded: {inserted_assessments}\n")
    
    # ========== SEED KB CARDS ==========
    print("📚 SEEDING 30 KNOWLEDGE BASE CARDS")
    print("-" * 80)
    
    inserted_cards = 0
    skipped_cards = 0
    
    for idx, card_data in enumerate(KB_CARDS_DATA, 1):
        try:
            existing = db.query(KBCard).filter(KBCard.id == card_data['id']).first()
            
            if existing:
                print(f"⏭️  [{idx:2d}] Skipping: {card_data['id']} - {card_data['title'][:40]}")
                skipped_cards += 1
                continue
            
            card = KBCard(**card_data, created_at=datetime.now(), updated_at=datetime.now())
            db.add(card)
            
            print(f"✅ [{idx:2d}] Inserted: {card_data['id']} - {card_data['title'][:40]}")
            inserted_cards += 1
            
        except Exception as e:
            db.rollback()
            print(f"❌ [{idx:2d}] Error: {str(e)[:50]}")
    
    db.commit()
    print(f"\n✅ KB Cards seeded: {inserted_cards}")
    print(f"⏭️  KB Cards skipped: {skipped_cards}\n")
    
    # ========== SUMMARY ==========
    print("\n" + "="*80)
    print("📊 SEEDING SUMMARY")
    print("="*80)
    print(f"✅ Decisions inserted:        {inserted_decisions}/5")
    print(f"✅ Threat Assessments:        {inserted_assessments}/5")
    print(f"✅ KB Cards inserted:         {inserted_cards}/30")
    print(f"⏭️  KB Cards skipped:         {skipped_cards}")
    
    total_decisions = db.query(Decision).count()
    total_assessments = db.query(ThreatLiteAssessment).count()
    total_cards = db.query(KBCard).count()
    
    print(f"\n📊 TOTALS IN DATABASE:")
    print(f"📋 Decisions:                 {total_decisions}")
    print(f"⚠️  Threat Assessments:        {total_assessments}")
    print(f"📚 KB Cards:                  {total_cards}")
    print("="*80 + "\n")
    
    db.close()
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
