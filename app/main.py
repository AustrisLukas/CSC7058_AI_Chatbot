import streamlit as st
from services import openai_service
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="---->>> %(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

pages = {
    "Assistants": [
        st.Page("pages/pageA1_doc.py", title="  📚 DocuMind"),
        st.Page("pages/pageA2_web.py", title="  🌐 WebMind"),
        st.Page("pages/pageA3_doc.py", title="DocuMind.v2"),
        st.Page("pages/pageA4_doc_early.py", title="DocuMind_early"),
    ],
    "Settings": [
        st.Page("pages/pageB1_settings.py", title="⚙️ User Preferences"),
        st.Page("pages/pageB2_AIBehaviour.py", title="⚙️ AI Behaviour"),
    ],
}

pg = st.navigation(pages)
pg.run()
