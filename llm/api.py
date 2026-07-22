import streamlit as st
import requests

class RateLimitError(Exception):
    pass

def get_chat_response(chat_history, system_prompt):
    """Sends the conversation history to the Gemini API and returns the assistant response.

    Args:
        chat_history: List of dicts with 'role' and 'content' keys representing
                      the full conversation history.
        system_prompt: String containing the system prompt built by build_system_prompt.

    Returns:
        str: The assistant's response text.
    """
    api_key = st.secrets["GEMINI_API_KEY"]

    role_map = {"assistant": "model", "user": "user"}

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}",
        json={
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": role_map[m["role"]],
                    "parts": [{"text": m["content"]}]
                }
                for m in chat_history
            ]
        }
    )

    if response.status_code in (429, 503):
        raise RateLimitError("The AI service is temporarily busy. Please try again shortly.")
    if not response.ok:
        raise RateLimitError("The AI service is currently unavailable.")
    
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]