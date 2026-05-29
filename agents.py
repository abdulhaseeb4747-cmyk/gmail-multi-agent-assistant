# ============================================================
# agents.py
# All agents in one file:
#   - build_reader_agent()   → stateless, reads emails
#   - build_search_agent()   → stateless, searches emails
#   - build_writer_agent()   → HITL middleware on send
#   - build_coordinator()    → wraps sub-agents as @tools
#
# HIERARCHY:
#   Coordinator
#     @tool → reader_tool  → Reader Agent
#     @tool → search_tool  → Search Agent
#     @tool → writer_tool  → Writer Agent (HITL on send)
# ============================================================

import os
import uuid
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from prompts import (
    COORDINATOR_PROMPT,
    READER_PROMPT,
    SEARCH_PROMPT,
    WRITER_PROMPT,
)

load_dotenv()


# ── Shared LLM ────────────────────────────────────────────
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )


# ── Reader Agent ──────────────────────────────────────────
def build_reader_agent(reader_tools):
    """Stateless — reads and summarizes emails."""
    return create_agent(
        model=get_llm(),
        tools=reader_tools,
        system_prompt=READER_PROMPT,
    )


# ── Search Agent ──────────────────────────────────────────
def build_search_agent(search_tools):
    """Stateless — searches emails by query."""
    return create_agent(
        model=get_llm(),
        tools=search_tools,
        system_prompt=SEARCH_PROMPT,
    )


# ── Writer Agent ──────────────────────────────────────────
def build_writer_agent(writer_tools):
    """
    Stateful agent with HumanInTheLoopMiddleware.
    send_gmail_message → pauses for approve / reject.
    create_gmail_draft → auto-approved (safe).
    InMemorySaver is required for HITL pause/resume.
    """
    return create_agent(
        model=get_llm(),
        tools=writer_tools,
        system_prompt=WRITER_PROMPT,
        checkpointer=InMemorySaver(),
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "send_gmail_message": {
                        "allowed_decisions": ["approve", "reject"],
                    },
                    "create_gmail_draft": False,
                },
                description_prefix="📨 Email ready to send",
            )
        ],
    )


# ── Coordinator ───────────────────────────────────────────
def build_coordinator(reader_agent, search_agent, writer_agent):
    """
    Wraps each sub-agent as a @tool.
    The Coordinator LLM decides which tool to call at runtime.

    writer_tool handles:
    - Recipient validation (Python — guaranteed)
    - Recipient history check (Search Agent)
    - Tone collection (Python input — never delegated to LLM)
    - Composition (Writer Agent LLM)
    - HITL approval loop (caught inside the wrapper)
    """

    @tool
    def reader_tool(request: str) -> str:
        """
        Use this to read or summarize specific emails.
        Examples:
          'summarize my latest 5 emails'
          'read the email from John about the meeting'
        """
        result = reader_agent.invoke(
            {"messages": [{"role": "user", "content": request}]}
        )
        return result["messages"][-1].content

    @tool
    def search_tool(request: str) -> str:
        """
        Use this to search for emails.
        Examples:
          'find emails from ahmed@gmail.com'
          'what emails did I receive today'
          'search for emails about invoice last week'
        """
        result = search_agent.invoke(
            {"messages": [{"role": "user", "content": request}]}
        )
        return result["messages"][-1].content

    @tool
    def writer_tool(request: str) -> str:
        """
        Use this to compose, send, or draft emails.
        Handles recipient validation, tone, composition,
        and human approval before sending.
        Examples:
          'send a casual email to john@gmail.com saying hi'
          'draft a professional email to the team about delays'
        """

        # ── STEP 1: Get and validate recipient ────────────
        print("\n" + "=" * 50)
        print("           ✉️   EMAIL COMPOSER")
        print("=" * 50)

        while True:
            recipient = input("\n📧 Recipient email address: ").strip()
            try:
                valid = validate_email(recipient, check_deliverability=False)
                recipient = valid.normalized
                break
            except EmailNotValidError as e:
                print(f"   ❌ Invalid email: {e}. Try again.")

        # ── STEP 2: Check recipient history ───────────────
        print(f"\n🔍 Checking if '{recipient}' is known...")
        check_result = search_agent.invoke(
            {"messages": [{"role": "user", "content":
                f"Search sent emails to {recipient}. "
                f"How many times have I emailed this address? "
                f"If none found, say 'No emails found'."
            }]}
        )
        history = check_result["messages"][-1].content
        if "no emails found" in history.lower() or "no results" in history.lower():
            print(f"   ⚠️  NEW recipient — '{recipient}' not found in sent history.")
        else:
            print(f"   ✅ Known recipient — found in sent history.")

        # ── STEP 3: Confirm recipient ──────────────────────
        while True:
            confirm = input(f"\n✅ Confirm sending to '{recipient}'? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                break
            elif confirm in ["no", "n"]:
                while True:
                    new_recipient = input("📧 Enter correct email address: ").strip()
                    try:
                        valid = validate_email(new_recipient, check_deliverability=False)
                        recipient = valid.normalized
                        break
                    except EmailNotValidError as e:
                        print(f"   ❌ Invalid email: {e}. Try again.")
                break

        # ── STEP 4: Collect tone ───────────────────────────
        # Ask for tone here in Python so writer_agent never needs
        # to ask a clarifying question mid-flow.
        while True:
            tone = input("\n🎨 Tone? (professional / casual): ").strip().lower()
            if tone in ["professional", "casual"]:
                break
            print("   Please type 'professional' or 'casual'.")

        # ── STEP 5: Hand off to Writer Agent ──────────────
        # Writer agent has everything it needs — no clarifying questions.
        # Fresh thread per task — clean context each time.
        writer_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        full_request = (
            f"{request}\n"
            f"Recipient email: {recipient}\n"
            f"Tone: {tone}\n"
            f"Compose the email, show it clearly, "
            f"then call send_gmail_message."
        )

        response = writer_agent.invoke(
            {"messages": [{"role": "user", "content": full_request}]},
            config=writer_config,
            version="v2",
        )

        # ── STEP 6: HITL approval loop ────────────────────
        # Caught HERE inside the wrapper — not in main.py.
        # Loops until approved or cancelled.
        while hasattr(response, "interrupts") and response.interrupts:
            action = response.interrupts[0]

            print("\n" + "=" * 52)
            print("      📨  EMAIL PENDING YOUR APPROVAL")
            print("=" * 52)
            val = action.value
            if isinstance(val, dict) and "action_requests" in val:
                req = val["action_requests"][0]
                args = req.get("args", {})
                to = ", ".join(args.get("to", []))
                subject = args.get("subject", "(no subject)")
                message = args.get("message", "")
                print(f"\n  To      : {to}")
                print(f"  Subject : {subject}")
                print(f"\n  Body:")
                print("  " + "-" * 44)
                for line in message.split("\n"):
                    print(f"  {line}")
                print("  " + "-" * 44)
            else:
                print(val)
            print("=" * 52)
            print("\n  approve        → send as-is")
            print("  cancel         → discard")
            print("  anything else  → feedback to recompose\n")

            decision = input("You: ").strip()

            if not decision:
                continue

            if decision.lower() in ["approve", "yes", "y"]:
                response = writer_agent.invoke(
                    Command(resume={"decisions": [{"type": "approve"}]}),
                    config=writer_config,
                    version="v2",
                )
            elif decision.lower() in ["cancel", "no", "n"]:
                response = writer_agent.invoke(
                    Command(resume={"decisions": [
                        {"type": "reject", "message": "cancel, do not send"}
                    ]}),
                    config=writer_config,
                    version="v2",
                )
                return "❌ Email cancelled. Nothing was sent."
            else:
                # Feedback — append as new HumanMessage so agent recomposes with full context.
                # version="v2" is required so the next send_gmail_message call triggers HITL.
                response = writer_agent.invoke(
                    {"messages": [{"role": "user", "content": decision}]},
                    config=writer_config,
                    version="v2",
                )

        return response.value["messages"][-1].content if hasattr(response, "value") else response["messages"][-1].content

    # ── Build Coordinator ──────────────────────────────────
    return create_agent(
        model=get_llm(),
        tools=[reader_tool, search_tool, writer_tool],
        system_prompt=COORDINATOR_PROMPT,
        checkpointer=InMemorySaver(),
    )