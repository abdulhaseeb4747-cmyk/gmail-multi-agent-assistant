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
        SystemContext[System Context<br/><b>Multi-Agent Security Architecture</b>]:::startContext
    end

    subgraph TerminalCluster [User Interaction Layer]
        UserTerminal[User Terminal CLI<br/>Send casual email to...]:::startContext
        UserActionChoice{<br/>User Action<br/>&nbsp;}:::decision
    end

    subgraph Orchestration [AI Orchestration Layer]
        Coordinator[COORDINATOR AGENT<br/>Supervisor/Router]:::orchestration
        StateCheckpointer[State Checkpointer<br/>InMemorySaver]:::orchestration
        LangGraph[LangGraph<br/>Checkpointer Config]:::orchestration
    end

    subgraph AgentExecution [Agent Execution Layer]
        WriterAgent[WRITER AGENT (Stateful)<br/>Drafting drafts with tools]:::agent
        ReaderAgent[READER AGENT (Stateless)<br/>Summarizing mails]:::agent
        SearchAgent[SEARCH AGENT (Stateless)<br/>Querying mailbox]:::agent
    end

    subgraph DefensiveControls [Defensive Guardrail Layer]
        Validation[DEFENSIVE INPUT VALIDATION<br/>validate_email()]:::defensive
        HITLGuardrail[HITL Guardrail<br/>Interceptor Middleware]:::defensive
    end

    subgraph OutputCluster [Execution / Egress Layer]
        GmailAPI[Gmail API<br/>Execute Send]:::output
        TrashBin[Trash Bin<br/>Terminate Workflow]:::output
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