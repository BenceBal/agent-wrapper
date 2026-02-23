# Product Requirements Document (PRD): Agent Wrapper

## 1. Vision
Build a **Multi-Agent Coding Framework** that acts as a "Meta-Developer".
Instead of just "generating code", it orchestrates specialized agents (Planner, Coder, Reviewer, Memory) to solve complex tasks autonomously.
It mimics a human dev team: it plans (Jira/Linear), executes (VS Code/Terminal), reviews (GitHub), and learns (Memory).

## 2. Core Features

### 2.1. The Orchestrator (The Brain)
-   **Input:** Natural Language ("Build a YouTube summarizer").
-   **Process:**
    1.  **System Design:** Breaks request into User Stories & Technical Specs.
    2.  **Task Queue:** Pushes tasks to specialized agents (e.g., "Set up repo", "Write backend", "Write frontend").
    3.  **Review Loop:** Agents critique each other's work before finalizing.

### 2.2. Context Management (The Memory)
-   **Short-Term:** Active window context (using `LLMLingua` compression).
-   **Long-Term:** Project-specific RAG (Vector DB) + Global Knowledge (User preferences).
-   **Tool:** `OneContext` integration.

### 2.3. Tooling (The Hands)
-   **Protocol:** **MCP (Model Context Protocol)** support.
    -   Connects to local Filesystem, GitHub, PostgreSQL, Linear/Jira.
-   **Optimization:** **DSPy** for self-improving prompts.

### 2.4. Interface (The Skin)
-   **Primary:** CLI / TUI (Terminal UI).
-   **Voice:** `VibeVoice` integration for hands-free instruction.
-   **IDE:** VS Code Extension (future).

## 3. Technical Architecture

### 3.1. Stack
-   **Language:** Python 3.11+
-   **Framework:** `LangGraph` (State Management) + `Pydantic` (Schema).
-   **LLM Interface:** `LiteLLM` (Universal wrapper for OpenAI/Anthropic/Local).
-   **Vector DB:** `ChromaDB` (Local) or `Qdrant`.

### 3.2. Agent Roles
1.  **Product Owner (PO):** Converts user request -> User Stories.
2.  **Architect:** Converts Stories -> Technical Design (Files, APIs).
3.  **Developer:** Writes code based on Specs.
4.  **QA/Reviewer:** Runs tests, checks style.

### 3.3. Data Flow
`User Request` -> `PO Agent` -> `Task Queue (Priority)` -> `Architect` -> `Dev Agents (Parallel)` -> `Reviewer` -> `Final Output`.

## 4. Roadmap
-   **Phase 1:** Core Framework (Orchestrator + Task Queue).
-   **Phase 2:** MCP Tool Integration (Filesystem, Git).
-   **Phase 3:** Memory Layer (RAG).
-   **Phase 4:** Voice & TUI.

## 5. Success Metrics
-   **Autonomy:** Can it build a "Hello World" Flask app without intervention?
-   **Efficiency:** Does it use fewer tokens than a naive chat loop?
-   **Quality:** Does the code pass linting/tests?
