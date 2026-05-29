# Secure Multi-Agent Gmail Assistant

A powerful multi-agent email orchestration system built using **LangChain** and **LangGraph**. This project automates reading, searching, and drafting emails via the Gmail API, utilizing a security-first architecture with strict human-in-the-loop guardrails.

---
## 🏗️ System Architecture & Program Flow

GitHub natively renders the flowchart below showing the exact logical data path, starting from your input to the final zero-trust verification checks:

```mermaid
graph LR
    %% Style Definitions
    classDef startContext fill:#222, stroke:#aaa, stroke-width:2px, color:#fff, text-align:center;
    classDef orchestration fill:#333, stroke:#55c, stroke-width:2px, color:#fff, text-align:center;
    classDef agent fill:#333, stroke:#c55, stroke-width:2px, color:#fff, text-align:center;
    classDef defensive fill:#333, stroke:#cc5, stroke-width:2px, color:#fff, text-align:center;
    classDef output fill:#333, stroke:#5c5, stroke-width:2px, color:#fff, text-align:center;
    classDef decision fill:#333, stroke:#aaa, stroke-width:2px, color:#fff, text-align:center;
    classDef invisible fill:none, stroke:none, color:none;

    subgraph Context [System Context Layer]
        SystemContext["System Context<br/><b>Multi-Agent Security Architecture</b>"]:::startContext
    end

    subgraph TerminalCluster [User Interaction Layer]
        UserTerminal["User Terminal CLI<br/>Send casual email to..."]:::startContext
        UserActionChoice{"User Action"}:::decision
    end

    subgraph Orchestration [AI Orchestration Layer]
        Coordinator["COORDINATOR AGENT<br/>Supervisor/Router"]:::orchestration
        StateCheckpointer["State Checkpointer<br/>InMemorySaver"]:::orchestration
        LangGraph["LangGraph<br/>Checkpointer Config"]:::orchestration
    end

    subgraph AgentExecution [Agent Execution Layer]
        WriterAgent["WRITER AGENT (Stateful)<br/>Drafting drafts with tools"]:::agent
        ReaderAgent["READER AGENT (Stateless)<br/>Summarizing mails"]:::agent
        SearchAgent["SEARCH AGENT (Stateless)<br/>Querying mailbox"]:::agent
    end

    subgraph DefensiveControls [Defensive Guardrail Layer]
        Validation["DEFENSIVE INPUT VALIDATION<br/>validate_email()"]:::defensive
        HITLGuardrail["HITL Guardrail<br/>Interceptor Middleware"]:::defensive
    end

    subgraph OutputCluster [Execution / Egress Layer]
        GmailAPI["Gmail API<br/>Execute Send"]:::output
        TrashBin["Trash Bin<br/>Terminate Workflow"]:::output
    end

    Context -...- TerminalCluster:::invisible
    UserTerminal -- "User Input Query" --> Coordinator
    Coordinator <--> StateCheckpointer
    Coordinator -- "uses" --> LangGraph
    Coordinator -- "routes task" --> WriterAgent
    Coordinator -- "routes task" --> ReaderAgent
    Coordinator -- "routes task" --> SearchAgent
    WriterAgent -- "Drafted Output" --> Validation
    Validation -- "validated draft" --> HITLGuardrail
    HITLGuardrail -- "PAUSED EXECUTION<br/>Wait for Human Approval" --> UserTerminal
    UserTerminal -- "Decision Choice" --> UserActionChoice
    UserActionChoice -- "APPROVE: Send As-Is" --> GmailAPI
    UserActionChoice -- "CANCEL: Stop Immediately" --> TrashBin
    UserActionChoice -- "FEEDBACK: Re-draft" --> WriterAgent

## 📂 Repository Structure

```text
├── agents.py          # Sub-agents & Coordinator definition + HITL wrapper logic
├── auth.py            # Gmail API OAuth initialization & tool partitioning
├── main.py            # Application entry point and user conversation loop
├── prompts.py         # Isolated system prompts for all agents
└── requirements.txt   # Application dependency configurations
```

---

## 🛡️ Key Security Features

### Defensive Routing

The `COORDINATOR AGENT` handles routing. The `Reader` and `Search` tools are kept entirely stateless and sandboxed so they cannot accidentally alter data or execute outbound actions.

### Deterministic Validation

Uses strict Python validation (`email-validator`) to verify recipient formats before allowing the LLM to execute actions, reducing hallucination-based risks.

### Zero-Trust Human-In-The-Loop (HITL)

High-risk actions like `send_gmail_message` are intercepted by LangGraph middleware. The system pauses execution, prints the full email to the terminal, and completely drops the workflow to the trash bin unless explicit human approval is given.

---

## 🚀 How to Run It Locally

### Prerequisites

* Python 3.10+
* A Google Cloud Project with the Gmail API enabled

---

## ⚙️ Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Add Google OAuth Credentials

Place your Google Cloud Desktop OAuth file in the project root directory and name it exactly:

```text
credentials.json
```

### 5. Run the Application

```bash
python main.py
```

---

## 🔐 First-Time Authentication Flow

On your first run:

1. A browser window will automatically open.
2. Sign into your Google account.
3. Grant Gmail permissions to the application.
4. A local `token.json` file will be generated automatically for future authenticated sessions.

---

## 🧠 Core Technologies

* LangChain
* LangGraph
* Gmail API
* Google OAuth 2.0
* Python
* Gemini API

---

## 📌 Design Philosophy

This project follows a **security-first multi-agent architecture**:

* Stateless read/search agents
* Strict tool partitioning
* Deterministic validation layers
* Human approval for high-risk actions
* Zero-trust execution flow
* Explicit orchestration boundaries

The goal is to demonstrate how modern LLM systems can safely interact with sensitive external systems like email infrastructure while maintaining strong operational safeguards.

---

## 📜 License

This project is intended for educational and research purposes.
