import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)
st.header("⚙️  AI Behaviour Settings", divider="grey")

col1, col2 = st.columns([5, 5])
with col1:
    with st.container(border=True):
        ai_response_style = st.radio(
            "AI Response Style",
            ["Concise", "Balanced", "Detailed"],
            captions=[
                "Short, direct answers. Focuses on key facts and conclusions",
                "Clear explanations with moderate detail. Avoids unnecessary verbosity",
                "In-depth explanations, includes context, assumptions, and edge cases",
            ],
            help="Select your preferred AI response style (e.g. concise, balanced, or detailed).",
            label_visibility="visible",
            index=1,
        )
        st.write("---")
        ai_creatvity = st.radio(
            "AI Creativity Adjustment",
            ["Strict", "Balanced", "Creative"],
            captions=[
                "Strictly grounded AI outputs.",
                "Combination of both.",
                "Outside source supplemented outputs.",
            ],
            index=0,
            help=(
                "Adjust the creativity of AI responses (temperature). "
                "Lower values produce more factual, deterministic output. "
                "Use 0 to ensure responses strictly follow the provided source."
            ),
            label_visibility="visible",
        )
    with col2:

        with st.container(border=True):
            st.write("Advanced")

            st.checkbox(
                "Use own API key",
                key="own_api_key",
                help=(
                    "Enter your OpenAI API key and select the model to use your own "
                    "OpenAI account and available credits."
                ),
                label_visibility="visible",
            )
            st.text_input("API Key", disabled=not st.session_state.own_api_key)
            st.selectbox(
                "OpenAI Model",
                (
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "o4-mini",
                    "o3-mini",
                    "text-embedding-3-large",
                    "text-embedding-3-small",
                    "whisper-1",
                    "dall-e-3",
                ),
                disabled=not st.session_state.own_api_key,
            )
            max_tokens = st.slider(
                "Max Tokens",
                min_value=50,
                max_value=3000,
                step=50,
                value=500,
                disabled=not st.session_state.own_api_key,
            )
