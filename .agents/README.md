# 🛡️ VajraNet Multi-Agent Orchestration Control Center

Welcome to the **VajraNet Multi-Agent Development System**. This directory (`.agents/`) is the central source of truth for coordinating 5 specialized development agents working across the integrated VajraNet emergency response ecosystem.

---

## 1. Directory Structure

```
.agents/
├── README.md                          # This control center documentation
│
├── orchestrator/
│   ├── AGENT.md                       # @orchestrator role definition & response standard
│   ├── RULES.md                       # 15 inviolable development & safety rules
│   ├── WORKFLOW.md                    # Cross-agent communication & dependency pipeline
│   └── STATE.md                       # Real-time multi-repo status & health tracking
│
├── backend/
│   └── AGENT.md                       # @backend-agent specification & boundaries
│
├── frontend/
│   └── AGENT.md                       # @frontend-agent specification (Gov EOC + Volunteer)
│
├── android/
│   └── AGENT.md                       # @android-agent specification (Native Kotlin & Mesh)
│
├── vajraai/
│   └── AGENT.md                       # @vajraai-agent specification (AI & Safety Guardrails)
│
├── docs/
│   └── AGENT.md                       # @docs-agent specification (Architecture & Cross-Repo QA)
│
├── shared/
│   ├── ARCHITECTURE.md                # System topology & tri-tier failover specs
│   ├── API_CONTRACT.md                # Authoritative REST API contracts
│   ├── DATA_MODELS.md                 # Database schemas, models & enums
│   ├── INTEGRATION_RULES.md           # Cross-repository interoperability rules
│   └── CHANGELOG.md                   # Ecosystem-wide change tracker
│
└── tasks/
    └── CURRENT.md                     # Active task tracker & agent progress
```

---

## 2. The 5 Repositories & Agent Ownership Matrix

| Agent Handle | Target Repository Location | Role & Primary Domain |
|---|---|---|
| **`@orchestrator`** | *All Repositories* | Master Coordinator & Single User Entry Point |
| **`@backend-agent`** | `C:/Users/Vansh/Desktop/projects/vajranet-backend` | FastAPI, Supabase PostgreSQL, Auth/RBAC, Gateway Sync, Authoritative State |
| **`@frontend-agent`** | `C:/Users/Vansh/Desktop/projects/vajranet-frontend` | React 18, Tactical EOC Command Center UI, Volunteer Field Operations Portal |
| **`@android-agent`** | `C:/Users/Vansh/Desktop/projects/demo-vajra` | Native Kotlin, Jetpack Compose, Room DB, Nearby Connections P2P Mesh |
| **`@vajraai-agent`** | `C:/Users/Vansh/Desktop/projects/VajraAI` | Emergency AI Engine, Groq/Gemini, Safety Guardrails, Resource Adapter |
| **`@docs-agent`** | `C:/Users/Vansh/Desktop/projects/vajranet-docs` | System Specs, API Docs, OFFLINE_P2P_TEST Runbooks, QA Observer |

---

## 3. How to Interact with the System

Developers interact exclusively with **`@orchestrator`**:

```text
@orchestrator <task description>
```

### Examples:
- `@orchestrator Implement Room database offline persistence in the Android app.`
- `@orchestrator Fix the government dashboard SOS status triage synchronization.`
- `@orchestrator Test the complete offline mesh to cloud gateway flow.`
- `@orchestrator Add a new emergency contact endpoint and integrate across Android and Web.`

The Orchestrator automatically inspects codebases, breaks tasks into subtasks, delegates to specialized agents in dependency order, coordinates API changes, runs automated test suites, validates integration, and produces a structured final report.
