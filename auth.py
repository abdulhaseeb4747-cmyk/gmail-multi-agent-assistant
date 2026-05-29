# ============================================================
# auth.py
# Gmail OAuth authentication + tool splitting.
# ============================================================

from langchain_google_community.gmail.utils import (
    build_gmail_service,
    get_google_credentials,
)
from langchain_google_community import GmailToolkit


def get_gmail_tools():
    """
    Authenticates with Gmail via OAuth.
    First run: opens browser for login, saves token.json.
    Future runs: reuses token.json automatically.
    Returns all Gmail tools from the toolkit.
    """
    credentials = get_google_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    api_resource = build_gmail_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    all_tools = toolkit.get_tools()

    print("\n📦 Available Gmail tools:")
    for t in all_tools:
        print(f"   - {t.name}")
    print()

    return all_tools


def split_tools(all_tools):
    """
    Splits Gmail tools into three groups for the sub-agents.
    Returns: (reader_tools, search_tools, writer_tools)
    """
    reader_tools = [t for t in all_tools if t.name in (
        "get_gmail_message", "get_gmail_thread"
    )]
    search_tools = [t for t in all_tools if t.name in (
        "search_gmail",
    )]
    writer_tools = [t for t in all_tools if t.name in (
        "send_gmail_message", "create_gmail_draft"
    )]
    return reader_tools, search_tools, writer_tools
