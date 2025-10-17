# main_app.py
import streamlit as st
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import agent dari file lain
from agents.agent import mix_match_agent

from dotenv import load_dotenv
load_dotenv()

# Konstanta session
APP_NAME = "MyStreamlitAgentApp"
USER_ID = "user_1"
SESSION_ID = "session_1"

# Setup session service dan runner
session_service = InMemorySessionService()
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

runner = Runner(agent=mix_match_agent, app_name=APP_NAME, session_service=session_service)

# UI Streamlit
st.title("🍹 Mix & Match Minuman")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history as speech bubbles.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.container()  # Fix ghost message bug.

        st.markdown(message["content"])

if query := st.chat_input("Masukan bahan-bahan yang ingin dijadikan minuman:"):
    if query.strip():
        # Display message as a speech bubble.
        with st.chat_message("user"):
            st.markdown(query)
            
        # Proses agent di dalam spinner, output langsung disimpan di response
        response = ""
        with st.chat_message("assistant"):
            with st.spinner("Thinking ..."):
                content = types.Content(role='user', parts=[types.Part(text=query)])
                events = runner.run(
                    user_id=USER_ID,
                    session_id=SESSION_ID,
                    new_message=content
                )
                
                for event in events:
                    if event.is_final_response():
                        text_parts = [p.text for p in event.content.parts if hasattr(p, "text")]
                        response += "\n".join(text_parts) + "\n"

            # Tampilkan hasil final
            if response != "":
                st.markdown(response)
                st.session_state.messages.append({"role": "user", "content": query})
                st.session_state.messages.append({"role": "assistant", "content": response})