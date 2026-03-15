# TechCorp Customer Success AI Agent - Incident Response Runbook

**Version:** 1.0.0  
**Last Updated:** January 2025  
**On-Call Rotation:** AI Engineering Team

---

## Quick Reference

| Emergency | Contact | Escalation |
|-----------|---------|------------|
| System Down | oncall@techcorp.com | VP Engineering |
| Security Incident | security@techcorp.com | CISO |
| Data Breach | legal@techcorp.com | Legal Team |

---

## System Health Checks

### Check Pod Status

```bash
# Check all pods in namespace
kubectl get pods -n customer-success-fte

# Check specific deployment
kubectl get pods -l component=api -n customer-success-fte
kubectl get pods -l component=message-processor -n customer-success-fte

# Watch pod status in real-time
kubectl get pods -n customer-success-fte -w
```

### Check Logs

```bash
# API logs
kubectl logs -f deployment/fte-api -n customer-success-fte

# Worker logs
kubectl logs -f deployment/fte-message-processor -n customer-success-fte

# Last 100 lines
kubectl logs --tail=100 deployment/fte-api -n customer-success-fte

# Search for errors
kubectl logs deployment/fte-api -n customer-success-fte | grep -i error
```

### Check Resource Usage

```bash
# Check CPU/memory usage
kubectl top pods -n customer-success-fte

# Check node resources
kubectl top nodes

# Check HPA status
kubectl get hpa -n customer-success-fte
```

### Check Database

```bash
# Connect to PostgreSQL
kubectl exec -it deployment/postgres -n customer-success-fte -- psql -U fte_user -d fte_db

# Check connection count
SELECT count(*) FROM pg_stat_activity;

# Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### Check Kafka

```bash
# Connect to Kafka container
kubectl exec -it deployment/kafka -n kafka -- /bin/bash

# List topics
kafka-topics --bootstrap-server localhost:9092 --list

# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group fte-message-processor
```

---

## Incident Playbooks

### Pod Crashes (CrashLoopBackOff)

**Symptoms:**
- `kubectl get pods` shows `CrashLoopBackOff`
- Pod restarts repeatedly

**Diagnosis:**
```bash
# Check pod events
kubectl describe pod <pod-name> -n customer-success-fte

# Check logs from previous instance
kubectl logs <pod-name> -n customer-success-fte --previous

# Check environment variables
kubectl exec <pod-name> -n customer-success-fte -- env
```

**Resolution:**
1. Identify root cause from logs
2. Fix configuration issue
3. Delete pod to force restart:
   ```bash
   kubectl delete pod <pod-name> -n customer-success-fte
   ```
4. If issue persists, rollback deployment:
   ```bash
   kubectl rollout undo deployment/fte-api -n customer-success-fte
   ```

**Escalation:** If unable to resolve in 15 minutes, escalate to Senior Engineer.

---

### Kafka Consumer Lag Spikes

**Symptoms:**
- Messages backing up in Kafka topics
- Increased response times
- Consumer lag > 1000 messages

**Diagnosis:**
```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server kafka:9092 \
    --describe --group fte-message-processor

# Check worker logs for errors
kubectl logs -f deployment/fte-message-processor -n customer-success-fte | grep -i error

# Check worker CPU/memory
kubectl top pods -l component=message-processor -n customer-success-fte
```

**Resolution:**
1. Scale up message processors:
   ```bash
   kubectl scale deployment fte-message-processor \
       --replicas=10 -n customer-success-fte
   ```
2. Check for processing errors in logs
3. If database is bottleneck, scale PostgreSQL
4. Monitor lag until it decreases

**Escalation:** If lag doesn't decrease after 30 minutes, escalate to Platform Team.

---

### Database Connection Exhausted

**Symptoms:**
- Errors: "too many connections", "connection pool exhausted"
- API returns 500 errors
- Slow query performance

**Diagnosis:**
```bash
# Check current connections
kubectl exec -it deployment/postgres -n customer-success-fte -- \
    psql -U fte_user -d fte_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check max connections
kubectl exec -it deployment/postgres -n customer-success-fte -- \
    psql -U fte_user -d fte_db -c "SHOW max_connections;"

# Check connection per application
kubectl exec -it deployment/postgres -n customer-success-fte -- \
    psql -U fte_user -d fte_db -c \
    "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
```

**Resolution:**
1. Identify connection leak source from logs
2. Restart application pods to release connections:
   ```bash
   kubectl rollout restart deployment/fte-api -n customer-success-fte
   kubectl rollout restart deployment/fte-message-processor -n customer-success-fte
   ```
3. If persistent, increase max_connections in PostgreSQL config
4. Consider adding connection pooler (PgBouncer)

**Escalation:** If unable to resolve in 20 minutes, escalate to DBA Team.

---

### WhatsApp Webhook Fails

**Symptoms:**
- Twilio returns errors
- Messages not being processed
- 403/500 errors in logs

**Diagnosis:**
```bash
# Check Twilio webhook logs
# Go to https://console.twilio.com > Messaging > Logs

# Check WhatsApp handler logs
kubectl logs -f deployment/fte-api -n customer-success-fte | grep -i whatsapp

# Check Twilio credentials
kubectl get secret fte-secrets -n customer-success-fte -o jsonpath='{.data.TWILIO_AUTH_TOKEN}' | base64 -d
```

**Resolution:**
1. Verify Twilio credentials are valid
2. Check webhook URL in Twilio console matches ingress
3. Verify SSL certificate is valid:
   ```bash
   curl -I https://support-api.yourdomain.com/webhooks/whatsapp
   ```
4. Check Twilio signature validation is working
5. Restart API pod if needed

**Escalation:** If Twilio-side issue, contact Twilio Support.

---

### Gmail Push Stops Working

**Symptoms:**
- No new emails being processed
- Gmail webhook returns errors
- Pub/Sub subscription shows no messages

**Diagnosis:**
```bash
# Check Gmail API status
kubectl logs -f deployment/fte-api -n customer-success-fte | grep -i gmail

# Check Pub/Sub subscription
gcloud pubsub subscriptions describe fte-gmail-sub

# Check service account credentials
kubectl exec -it deployment/fte-api -n customer-success-fte -- \
    cat /app/credentials/google.json | head -5
```

**Resolution:**
1. Verify service account credentials are valid
2. Check Gmail API is enabled in Google Cloud Console
3. Re-setup Gmail watch:
   ```python
   # Run setup script
   python -c "from production.channels.gmail_handler import GmailHandler; \
              h = GmailHandler('credentials.json'); \
              import asyncio; asyncio.run(h.setup_push_notifications('fte-gmail-notifications'))"
   ```
4. Check Pub/Sub subscription push endpoint is reachable

**Escalation:** If Google-side issue, contact Google Cloud Support.

---

### Escalation Queue Backs Up

**Symptoms:**
- Escalation tickets not being assigned
- Customer complaints about no response
- Queue depth increasing

**Diagnosis:**
```bash
# Check escalation count
kubectl exec -it deployment/postgres -n customer-success-fte -- \
    psql -U fte_user -d fte_db -c \
    "SELECT count(*) FROM tickets WHERE status='escalated';"

# Check escalation topic lag
kafka-consumer-groups --bootstrap-server kafka:9092 \
    --describe --group fte-escalation-processor

# Check escalation worker logs
kubectl logs -f deployment/fte-message-processor -n customer-success-fte | grep -i escalation
```

**Resolution:**
1. Scale up escalation processors
2. Check email/Slack integration for human notifications
3. Manually notify on-call team via PagerDuty
4. Consider temporary manual triage

**Escalation:** Immediately notify Support Team Lead.

---

## On-Call Escalation Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| Primary On-Call | [TBD] | [TBD] | oncall-primary@techcorp.com |
| Secondary On-Call | [TBD] | [TBD] | oncall-secondary@techcorp.com |
| VP Engineering | [TBD] | [TBD] | vp-eng@techcorp.com |
| CISO | [TBD] | [TBD] | ciso@techcorp.com |

---

## Rollback Procedure

### Rollback API Deployment

```bash
# Check rollout history
kubectl rollout history deployment/fte-api -n customer-success-fte

# Rollback to previous version
kubectl rollout undo deployment/fte-api -n customer-success-fte

# Rollback to specific revision
kubectl rollout undo deployment/fte-api -n customer-success-fte --to-revision=2

# Watch rollback progress
kubectl rollout status deployment/fte-api -n customer-success-fte
```

### Rollback Worker Deployment

```bash
# Check rollout history
kubectl rollout history deployment/fte-message-processor -n customer-success-fte

# Rollback to previous version
kubectl rollout undo deployment/fte-message-processor -n customer-success-fte

# Watch rollback progress
kubectl rollout status deployment/fte-message-processor -n customer-success-fte
```

### Emergency Full Rollback

```bash
# Rollback all deployments
kubectl rollout undo deployment -n customer-success-fte

# Verify all pods are running
kubectl get pods -n customer-success-fte

# Verify health endpoint
curl https://support-api.yourdomain.com/health
```

---

## Post-Incident Checklist

After resolving any incident:

- [ ] Document timeline of events
- [ ] Identify root cause
- [ ] Create Jira ticket for permanent fix
- [ ] Update runbook if needed
- [ ] Send incident report to stakeholders
- [ ] Schedule post-mortem meeting

---

**End of Runbook**
