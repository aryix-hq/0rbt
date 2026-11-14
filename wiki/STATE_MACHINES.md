# Living State Machines & Lifecycle Specifications

> **Custodian**: System Architect & Full Stack Developer (`@architect`, `@fullstack-developer`)  
> **Status**: Living State Specification  
> **Last Synchronized**: 2026-10-21  

This document tracks all formal state machines, transition guards, terminal states, and concurrency lock invariants across the application.

---

## 1. Feature & Sprint Engineering Lifecycle (4-Stage Mandate)

```mermaid
stateDiagram-v2
    [*] --> Stage1_Research: User Need / Domain Spike
    Stage1_Research --> Stage2_ProductScoping: RES-XXX Markdown Verified
    Stage2_ProductScoping --> Stage3_Planning: FEAT-XXX & RICE Prioritized
    Stage3_Planning --> Stage4_Execution: PLAN-XXX & UML Signed Off
    
    state Stage4_Execution {
        [*] --> InDevelopment: Branch feat/*
        InDevelopment --> ZeroMockTesting: Automated Container Tests
        ZeroMockTesting --> DefectLogging: Regression Detected (DEF-XXX)
        DefectLogging --> InDevelopment: Remediation Fix
        ZeroMockTesting --> PreviewDeploy: Tests Green
        PreviewDeploy --> EM_Review: bin/deploy-preview.sh Passed
    }

    Stage4_Execution --> MergedToMain: EM PR Approval & Merge
    MergedToMain --> Released: bin/release.sh (Tag & GitHub Release)
    Released --> [*]
```

---

## 2. Transactional Outbox Event Publishing Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: DB Transaction Committed
    Pending --> Publishing: Worker Acquired Lock
    Publishing --> Published: Broker ACK Received
    Publishing --> Retrying: Network Timeout / Broker Unavailable
    
    state Retrying {
        [*] --> BackoffWait
        BackoffWait --> NextAttempt: Retry Counter < 5
    }
    
    NextAttempt --> Publishing
    Retrying --> DeadLetterQueue: Retry Counter >= 5
    Published --> Pruned: Retention Period Expired
    DeadLetterQueue --> ManualIntervention: Incident Logged (INC-XXX)
    Pruned --> [*]
```

---

## 3. Production Release & Rollback Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PreFlightGating: bin/release.sh Triggered
    PreFlightGating --> Aborted: Dirty Tree / Leaked Secrets / Test Failure
    PreFlightGating --> SemVerCalculation: All Gates Passed
    SemVerCalculation --> ChangelogSlicing: [Unreleased] Extracted
    ChangelogSlicing --> TaggingAndPush: Commit & Annotated Tag Created
    TaggingAndPush --> RemotePublication: GitHub Release Published
    
    state ProductionMonitoring {
        [*] --> CanaryObservation
        CanaryObservation --> Healthy: Metrics & Healthchecks Green
        CanaryObservation --> DegradationDetected: Errors Spiking / Healthchecks Red
    }
    
    RemotePublication --> ProductionMonitoring
    Healthy --> ActiveRelease: Release Complete
    ActiveRelease --> [*]

    DegradationDetected --> EmergencyRollback: Trigger Rollback Runbook
    EmergencyRollback --> PriorStableTag: git checkout ROLLBACK_TARGET
    PriorStableTag --> MainRevertPR: Revert Commit Merged to main
    MainRevertPR --> [*]
```

---

## 4. State Transition & Concurrency Invariants
1. **Deterministic State Guards**: An entity can never jump states without satisfying explicit guard conditions (e.g. no release without pre-flight green gates).
2. **Optimistic Locking**: Every mutable aggregate maintains an integer `version` field. State transitions verify `WHERE version = :current_version`.
3. **Dead-Letter Invariants**: Failed asynchronous transitions that exceed retry thresholds transition to `DeadLetterQueue` with an immutable failure payload and alert `@devops-sre`.

