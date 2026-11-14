# Living Deployment & Operations Runbook

> **Custodian**: DevOps & Site Reliability Engineer (`@devops-sre`)  
> **Status**: Living Deployment Specification  
> **Last Synchronized**: 2026-10-21  

This document details container configurations, preview deployment lifecycles, healthchecks, environment variables, zero-downtime release procedures, and dual-scale deployment models (laptop vs. enterprise cloud).

---

## 1. Dual-Scale Deployment Architecture

The software is engineered with a **Dual-Scale Deployment Model**: identical application code runs seamlessly on a developer's laptop ($0 cost, <2GB RAM) or scales out to an enterprise Kubernetes multi-AZ cluster.

| Dimension | Profile 1: Developer Laptop / Self-Managed VPS | Profile 2: Enterprise Cloud Scale |
| :--- | :--- | :--- |
| **Target Infrastructure** | Single laptop (macOS/Linux) or $5-10/mo VPS | Multi-AZ Kubernetes (EKS / GKE / AKS / Kubeadm) |
| **Compute Packaging** | Lightweight Docker Compose (`docker compose up -d`) | Helm Charts, PodDisruptionBudgets & HPA Autoscaling |
| **Relational SQL** | Single PostgreSQL 16 container (`< 512MB` RAM) | Multi-AZ PostgreSQL 16 + Read Replicas + PgBouncer |
| **NoSQL & Cache** | Single Redis 7 container (`< 128MB` RAM) | Multi-node Redis 7 Cluster with Sentinel Failover |
| **Streaming / Queue** | Redis Streams (`XADD`/`XREADGROUP`, `< 20MB` RAM) | Distributed Apache Kafka or RabbitMQ Cluster with DLX |
| **Secret Management** | Local `.env` or single Vault container | HashiCorp Vault AppRole dynamic credentials & KMS |
| **Observability** | Structured JSON to stdout + optional local Prometheus | OpenTelemetry Collector DaemonSet, Tempo, Loki, Grafana |
| **Total System RAM** | **< 2 GB Total Footprint** | Elastic auto-scaling to thousands of concurrent cores |

---

## 2. Safe Branch Preview Deploy Strategy

The deployment engine (`bin/deploy-preview.sh`) guarantees that feature work is built and verified in ephemeral containers without touching `main`.

### Usage
```bash
# Preview current branch on default port (8080)
./bin/deploy-preview.sh

# Deploy specific branch on custom port
./bin/deploy-preview.sh feat/FEAT-042 8090

# Test-and-exit mode (used in CI/CD and pre-PR verification)
./bin/deploy-preview.sh feat/FEAT-042 8090 --test-and-exit
```

---

## 2. Environment & Container Naming Convention

Container names are strictly differentiated to prevent collisions between production and branch previews:

| Environment | Branch | Container Name Pattern | Example |
| :--- | :--- | :--- | :--- |
| **Production** | `main` / `master` | `<project>-main-<port>` | `ai-agents-main-8080` |
| **Branch Preview** | `feat/*`, `fix/*` | `<project>-preview-<branch-slug>-<port>` | `ai-agents-preview-feat-feat-042-8090` |

---

## 3. Environment Variables & Secret Management

| Variable Name | Purpose | Required In | Default / Example |
| :--- | :--- | :---: | :--- |
| `PORT` | HTTP Server port | All | `8080` |
| `NODE_ENV` | Runtime environment (`production` / `development`) | All | `production` |
| `DATABASE_URL` | PostgreSQL connection string | Prod & Preview | `postgresql://app:pass@db:5432/app` |
| `OLLAMA_HOST` | Local Ollama inference daemon endpoint | Worker / Dev | `http://127.0.0.1:11434` |

---

## 4. Healthcheck & Rollback Runbook
* **Health Endpoint**: `GET /healthz` (Must respond within 200ms with HTTP 200).
* **Rollback Trigger**: If healthcheck fails 3 consecutive times post-deploy, trigger automatic rollback to previous container tag.

