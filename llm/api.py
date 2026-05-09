import streamlit as st
import requests

def get_chat_response(chat_history, system_prompt):
    """Sends the conversation history to the Groq API and returns the assistant response.

    Args:
        chat_history: List of dicts with 'role' and 'content' keys representing
                      the full conversation history.
        system_prompt: String containing the system prompt built by build_system_prompt.

    Returns:
        str: The assistant's response text.
    """
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 1024,
            "messages": [{"role": "system", "content": system_prompt}] + chat_history
        }
    )

    if not response.ok:
        st.error(response.json())
        response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]