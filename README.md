# Multi-Agent Gmail Assistant (LangChain Demonstration)

A hands-on project built to explore and demonstrate the core capabilities of the **LangChain** framework. This application automates reading, searching, and drafting emails via the Gmail API while showcasing a practical implementation of the supervisor/worker orchestration pattern and a custom Human-in-the-Loop (HITL) approval workflow.

---

# 🏗️ System Architecture & Logic Flow

The flowchart below illustrates how the application routes requests through a central LangChain supervisor before pausing for explicit user confirmation prior to executing outbound email actions.

```mermaid id="1axmq1"
graph LR
    %% Style Definitions
    classDef startContext fill:#222,stroke:#aaa,stroke-width:2px,color:#fff;
    classDef orchestration fill:#333,stroke:#55c,stroke-width:2px,color:#fff;
    classDef agent fill:#333,stroke:#c55,stroke-width:2px,color:#fff;
    classDef control fill:#333,stroke:#cc5,stroke-width:2px,color:#fff;
    classDef output fill:#333,stroke:#5c5,stroke-width:2px,color:#fff;
    classDef decision fill:#333,stroke:#aaa,stroke-width:2px,color:#fff;
    classDef invisible fill:none,stroke:none,color:none;

    subgraph Context["Project Context"]
        SystemContext["Framework Demo<br/><b>LangChain Core Concepts</b>"]:::startContext
    end

    subgraph Terminal["User Interface"]
        UserTerminal["User Terminal CLI<br/>Prompt: 'Send email to...'"]:::startContext
        UserAction{"User Action"}:::decision
    end

    subgraph Orchestration["Orchestration Layer"]
        Coordinator["COORDINATOR AGENT<br/>LangChain Supervisor / Router"]:::orchestration
    end

    subgraph Agents["Sub-Agents"]
        WriterAgent["WRITER AGENT<br/>Drafts email body"]:::agent
        ReaderAgent["READER AGENT<br/>Reads / Summarizes"]:::agent
        SearchAgent["SEARCH AGENT<br/>Queries mailbox"]:::agent
    end

    subgraph Guardrail["Review Loop"]
        HITLStep["Human-in-the-Loop<br/>Console Interrupt"]:::control
    end

    subgraph Output["Execution / Egress"]
        GmailAPI["Gmail API<br/>Execute Send"]:::output
        TrashBin["Workflow Terminated<br/>Clear State"]:::output
    end

    Context -...- Terminal:::invisible

    UserTerminal --> Coordinator

    Coordinator -->|"Delegates"| WriterAgent
    Coordinator -->|"Delegates"| ReaderAgent
    Coordinator -->|"Delegates"| SearchAgent

    WriterAgent -->|"Drafted Email"| HITLStep

    HITLStep -->|"Display Draft & Pause"| UserTerminal

    UserTerminal -->|"Selection"| UserAction

    UserAction -->|"APPROVE"| GmailAPI
    UserAction -->|"CANCEL"| TrashBin
    UserAction -->|"FEEDBACK"| WriterAgent
```

---

# 📂 Repository Structure

```text id="jlwm3r"
├── agents.py
│   └── Sub-agents, supervisor routing, and terminal HITL workflow
│
├── auth.py
│   └── Gmail API OAuth initialization and tool loading
│
├── main.py
│   └── Main application entry point and interactive CLI loop
│
├── prompts.py
│   └── System prompts defining individual agent behavior
│
└── requirements.txt
    └── Core project dependencies
```

---

# ⚙️ Core Concepts Demonstrated

## Supervisor Pattern

Demonstrates how a central LangChain orchestration agent can:

* Parse user intent
* Delegate execution
* Coordinate specialized worker agents
* Maintain workflow control

---

## Tool Integration

Connects LLM-driven agents directly to external Gmail tools for:

* Reading emails
* Searching mailboxes
* Drafting email responses
* Staging outbound actions

---

## Human-in-the-Loop (HITL)

Implements a conditional terminal approval workflow that intercepts high-impact actions such as:

```python id="ecw95p"
send_gmail_message
```

Before execution, the system:

1. Prints the drafted email
2. Pauses execution
3. Requires explicit user approval

Available actions:

* APPROVE
* CANCEL
* FEEDBACK / REVISE

---

# 🚀 How to Run Locally

## Prerequisites

* Python 3.10+
* Google Cloud Project
* Gmail API enabled
* OAuth Desktop credentials configured

---

# ⚙️ Installation

## 1. Clone the Repository

```bash id="hmv4a8"
git clone https://github.com/yourusername/your-repository-name.git

cd your-repository-name
```

---

## 2. Install Dependencies

```bash id="4v5nxa"
pip install -r requirements.txt
```

---

## 3. Create a `.env` File

```env id="jlwmqj"
GEMINI_API_KEY=your_gemini_api_key
```

---

## 4. Add OAuth Credentials

Place your Google Cloud OAuth Desktop credentials file in the root directory and rename it to:

```text id="0af40r"
credentials.json
```

---

## 5. Run the Application

```bash id="m8hkn7"
python main.py
```

---

# 🔐 First-Time Authentication

On the first launch:

1. A browser window opens automatically
2. Sign into your Google account
3. Approve Gmail API permissions
4. A local `token.json` file is generated for persistent authentication

---

# 🧠 Technologies Used

* LangChain
* Gmail API
* Google OAuth 2.0
* Gemini API
* Python

---

# 📌 Project Purpose

This repository was built as a practical learning project to explore:

* Multi-agent orchestration
* Tool-calling workflows
* LLM supervision patterns
* Safe external system interaction
* Human approval loops

The focus is educational and architectural rather than production deployment.

---

# 📜 License

This project is intended for:

* Educational purposes
* Research
* LangChain experimentation
* Multi-agent workflow demonstrations

Use responsibly and comply with Google's API Terms of Service.
