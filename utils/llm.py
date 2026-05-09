import streamlit as st
import requests

def get_chat_response(chat_history, system_prompt):
    """Sends the conversation history to the Anthropic API and returns the assistant response.

    Args:
        chat_history: List of dicts with 'role' and 'content' keys representing
                      the full conversation history.
        system_prompt: String containing the system prompt built by build_system_prompt.

    Returns:
        str: The assistant's response text.
    """
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": st.secrets["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": chat_history
        }
    )

    response.raise_for_status()
    return response.json()["content"][0]["text"]