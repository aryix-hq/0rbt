# Datadog: .NET Continuous Profiler: CPU and wall time profiling | Datadog

> **Canonical URL**: https://www.datadoghq.com/blog/engineering/dotnet-continuous-profiler-part-2  
> **Pattern**: Thread Sampling  
> **Hash**: `a25262c800aa61e83f1240d39c5c7a3a50d104da31d523d86bb49c2ca69ed5b7`  
> **Ingested**: 2026-11-14 15:38:34  

---

## 1. Executive Problem & Solution Breakdown
- **Problem**: Efficiently profiling CPU and wall time in .NET applications without impacting performance in production environments
- **Solution**: Datadog's .NET continuous profiler samples threads at a certain frequency to collect profiling data. It uses the .NET profiling API's enter/leave hooks to monitor managed threads and avoid sampling native threads. The profiler stores the list of managed threads and assigns durations to samples based on the call stack and context. This approach allows developers to identify slow methods and optimize their code without the need for intrusive tools.
- **Trade-offs**: The trade-off is between the accuracy of profiling data and the performance impact on the application. A higher sampling frequency provides more accurate data but may impact performance more significantly.
- **System Invariants**:
  - Only managed threads are sampled to avoid impacting the profiler's performance
  - Sampling frequency is adjusted to balance between data accuracy and performance impact

---

## 2. Big Tech vs. Lean Startup Client Playbook
- **Big Tech Overkill**: Copying Datadog's massive infrastructure is not feasible for a 5-50 engineer startup due to high costs and complexity
- **Small-Scale Client Architecture**: For small-scale applications, you can implement a similar thread sampling approach using open-source tools like dotnet-counters or custom scripts. These tools allow you to monitor CPU and wall time without the need for a full-fledged observability platform. By using simple workers and periodic sampling, you can achieve similar insights into your application's performance.
- **Estimated Savings**: Estimated monthly savings of $500-$2000 compared to using Datadog's enterprise SaaS solution, depending on the size and complexity of your application
- **Actionable Steps**:
  - Identify the key metrics you want to monitor (CPU, wall time, etc.)
  - Choose an open-source tool or script for thread sampling
  - Implement periodic sampling and store the data for analysis
  - Optimize your application based on the insights gained from profiling

---

## 3. LinkedIn Thought Leadership Drafts
### Hook 1 (Contrarian)
> Contrarian engineering insight breaking a common myth

### Hook 2 (Narrative)
> Narrative story hook describing the failure and re-architecture

### Post Body
```markdown
In the quest for efficient .NET applications, CPU and wall time profiling are essential tools. However, traditional methods like Event Tracing for Windows (ETW) or Linux perf can be too intrusive for production environments. Datadog's .NET continuous profiler offers a solution by sampling threads at a certain frequency without significantly impacting performance. This approach allows developers to identify bottlenecks and optimize their code without the need for high user privileges or system-wide impact. By understanding how threads are monitored and sampled, you can implement similar strategies in your own applications to enhance performance and reduce resource consumption.
```

---

## 4. ai-agents Codebase Evolution
- **Target Skills**: devops-sre, database-architect
- **Proposed Rule**: `INV-1234: Auto-Optimize Thread Sampling Configuration`
