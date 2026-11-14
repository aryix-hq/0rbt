# Memory & Feature Session Reset Rules

1. **Feature-Bound Sessions**:
   - Monolithic chats across multiple tickets or sprints are prohibited.
   - Limit each conversation session to a single feature (`FEAT-xxx`) or defect (`DEF-xxx`).

2. **Automated Session Reset Protocol**:
   - The orchestrating agent MUST automatically execute `ai-agents session reset --auto` upon completing Stage 4 Definition of Done or upon PR submission.
   - Never prompt the user to manually execute session resets in terminal.
   - The automated reset:
     1. Auto-detects the active ticket from Git branch, memory graph, or spec files.
     2. Archives short-term session state into `.agents/memory/sessions/`.
     3. Flushes status, milestones, and test results into `.agents/memory/memory_graph.json`.
     4. Resets `.agents/memory/active_feature.md` to a clean idle slate for the next ticket.
   - Once reset, the agent prompts the user to open a fresh chat or type `/compact`.

3. **Dual-Layer Memory Hierarchy**:
   - **Project Memory (`.agents/memory/`)**:
     - Scoped strictly to the active repository.
     - Tracks active feature, architecture decisions, component dependency graph, and local defect ledger.
   - **Global Memory (`ai-agents/memory/global/`)**:
     - Preserves cross-project patterns, proven libraries, shared anti-patterns, and emerging rule proposals.
     - Synced across machines via Git repository (`https://github.com/aryix-hq/ai-agents.git`).

4. **Continuous Learning**:
   - When encountering a novel defect, recurring trap, or architectural pattern, record it into global memory so all future project sessions inherit the insight.
