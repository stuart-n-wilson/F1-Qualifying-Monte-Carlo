import streamlit as st
import requests

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

    if not response.ok:
        st.error(response.json())
        response.raise_for_status()

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
