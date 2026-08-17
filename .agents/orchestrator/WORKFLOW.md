# 🔄 VajraNet Cross-Agent Coordination Workflow

## 1. Communication Flow Architecture

Agents in the VajraNet ecosystem do not modify other repositories directly. All cross-repository notifications and contract adjustments flow through the central orchestrator:

```
[Specialized Agent] (e.g. @backend-agent)
       │
       ▼ (Reports proposed contract change)
[@orchestrator]
       │
       ├─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
[@android-agent]  [@frontend-agent] [@vajraai-agent]
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                   [@docs-agent] (Updates Specs & Runbooks)
```

---

## 2. Standard Agent Report Format

Whenever an agent completes a subtask or proposes an architectural change, it reports to `@orchestrator` using this structured payload:

```markdown
### AGENT REPORT
- **Agent:** @backend-agent | @frontend-agent | @android-agent | @vajraai-agent | @docs-agent
- **Status:** COMPLETED | IN_PROGRESS | BLOCKED

### WHAT CHANGED
<Concise summary of code or schema modifications>

### WHY
<Emergency engineering rationale>

### FILES MODIFIED
- `path/to/file1.py`
- `path/to/file2.kt`

### API & SCHEMA IMPACT
<Details on new/updated endpoints, request/response models, or DB columns>

### DEPENDENCIES & CONSUMER ACTIONS
- **@android-agent:** Update Retrofit/HttpURLConnection payload model
- **@frontend-agent:** Adjust Axios response unwrap logic
- **@docs-agent:** Update 03_API_REFERENCE.md

### TEST STATUS
<Exact test command executed and result output>
```

---

## 3. Step-by-Step Change Pipeline

### Example Scenario: Backend Adds a New SOS Metadata Field

1. **Step 1 — Initiation:** User prompts `@orchestrator Add battery_level to SOS distress alerts`.
2. **Step 2 — Backend Contract Execution:**
   - `@orchestrator` assigns `@backend-agent`.
   - `@backend-agent` updates `app/schemas/sos.py`, `app/models/sos.py`, and `schema.sql`.
   - `@backend-agent` runs `pytest` and reports back to `@orchestrator`.
3. **Step 3 — Central Contract Synchronization:**
   - `@orchestrator` updates `.agents/shared/API_CONTRACT.md` and `.agents/shared/DATA_MODELS.md`.
4. **Step 4 — Client & Consumer Alignment:**
   - `@orchestrator` invokes `@android-agent` to include `battery_level` in `NearbyMessagePayload` and `VajraBackendClient.kt`.
   - `@orchestrator` invokes `@frontend-agent` to render battery percentage badge in the EOC Live SOS queue.
   - `@orchestrator` invokes `@vajraai-agent` to ensure AI chat context can read battery state.
5. **Step 5 — Documentation & QA Audit:**
   - `@orchestrator` invokes `@docs-agent` to update `03_API_REFERENCE.md` and `04_DATABASE_SCHEMA.md`.
6. **Step 6 — Integration & Final Report:**
   - `@orchestrator` executes cross-repository test suites and returns the final standardized response to the user.
