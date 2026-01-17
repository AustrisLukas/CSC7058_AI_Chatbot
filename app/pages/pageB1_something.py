import streamlit as st

# PAGE CONFIG
st.set_page_config(
    page_title="DocuMind",
    page_icon="app/assets/images/favicon_v2.png",
    layout="wide",
)


st.header("⚙️  User Preference Settings", divider="grey")

col1, col2 = st.columns([4, 6])

with col1:

    language = st.selectbox(
        "AI Response Language",
        (
            "English",
            "Spanish",
            "French",
            "German",
            "Portuguese",
            "Italian",
            "Chinese (Simplified)",
            "Japanese",
            "Korean",
            "Arabic",
            "Ukrainian",
            "Polish",
            "Czech",
            "Lithuanian",
            "Latvian",
        ),
        help=(
            "Select the language in which the AI should generate its responses."
            "This setting affects all text output from the AI, including summaries, explanations, and answers."
        ),
    )

    show_ref = st.checkbox(
        "Show Answer Confidence",
        help=(
            "Check this option to display the AI’s confidence or certainty in its answers. "
            "Higher confidence indicates the AI is more certain about the response."
        ),
        value=True,
    )
