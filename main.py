# ============================================================
# main.py
# Entry point — run this file to start the agent.
#
# FLOW:
#   1. Authenticate with Gmail
#   2. Split tools into groups
#   3. Build sub-agents + coordinator
#   4. Start conversation loop
#
# NOTE: HITL approval is handled inside agents.py writer_tool.
# main.py just runs the coordinator loop cleanly.
# ============================================================

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import get_gmail_tools, split_tools
from agents import (
    build_reader_agent,
    build_search_agent,
    build_writer_agent,
    build_coordinator,
)


def main():
    print("===========================================")
    print("     Gmail Multi-Agent - Terminal Mode     ")
    print("===========================================")
    print(" Reader | Search | Writer (HITL approval) ")
    print(" Type 'quit' or 'exit' to stop.           ")
    print("===========================================")

    # STEP 1 — Gmail auth
    print("\n🔐 Connecting to Gmail...")
    all_tools = get_gmail_tools()

    # STEP 2 — Split tools
    reader_tools, search_tools, writer_tools = split_tools(all_tools)

    # STEP 3 — Build agents
    print("🤖 Building agents...")
    reader_agent = build_reader_agent(reader_tools)
    search_agent = build_search_agent(search_tools)
    writer_agent = build_writer_agent(writer_tools)
    coordinator  = build_coordinator(reader_agent, search_agent, writer_agent)

    # STEP 4 — Conversation loop
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print("\n✅ Ready! How can I help with your emails?\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("\nAgent: Goodbye! Have a great day.")
            break

        if not user_input:
            continue

        response = coordinator.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        # Coordinator returns a plain dict — access messages directly
        reply = response["messages"][-1].content
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()