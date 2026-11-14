# Slack: Scaling Slack's Real-Time Message Bus: The Flannel Edge Cache

> **Organization**: Slack  
> **Domain**: Real-Time Collaboration & Distributed Caching  
> **Published**: 2022-04-18  
> **Source URL**: [https://slack.engineering/flannel-scaling-slacks-real-time-message-bus](https://slack.engineering/flannel-scaling-slacks-real-time-message-bus)  
> **Pattern**: `Edge Client Presence Caching & Multiplexed WebSocket Distribution`  

---

## 1. Problem Statement & Operational Dilemma
When large enterprise organizations (100k+ members) broadcasted messages, millions of connected WebSockets simultaneously fetched channel history and presence, overwhelming backend message databases.

---

## 2. Production Architecture & Solution Breakdown
Engineered Flannel, an in-memory edge caching proxy. Flannel sits between client WebSockets and central backend servers, multiplexing real-time updates and caching active channel state locally at the edge. Slashed backend read queries by over 80%.

### Enforced Invariants
- `INV-CACHE-01: Message delivery ordering must remain strictly sequential per channel via monotonic sequence IDs`
- `INV-CACHE-02: In-memory cache invalidation must be event-driven via pub/sub, not polling`

### Trade-offs & Operational Costs
Increased memory footprint at the edge and potential cache desynchronization during network partitions.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Deploying bespoke Go/C++ edge caching proxies for WebSockets is massive overkill for standard apps.
- **Pragmatic Small-Scale Architecture**: Use Redis Pub/Sub or Redis Streams with a Node.js or Go WebSocket gateway server.
- **Estimated Savings**: $8,000/mo in edge infrastructure and telemetry costs

### Actionable Implementation Checklist
1. Use Redis Pub/Sub for cross-node broadcast
1. Assign monotonic sequence IDs to messages
1. Implement client-side reconnect backoff

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-RES-03: Real-time broadcast systems must enforce monotonic ordering and decorrelated full jitter`
