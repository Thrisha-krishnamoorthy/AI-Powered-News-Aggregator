import streamlit as st
from chat_model import chat_with_gemini

def render():
    st.title("💬 Gemini Chat with Context Grounding")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    user_input = st.chat_input("Ask something...")
    print("fetch_grou   nded_context    ")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            response = chat_with_gemini(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
