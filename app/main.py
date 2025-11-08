import streamlit as st
from services import openai_service
import json

pages = {
    "Assistants": [
        st.Page("pages/page1_doc.py", title="DocuMind"),
        st.Page("pages/page2_web.py", title="WebMind"),
    ],
    "Settings": [
        st.Page("pages/page3_something.py", title="Page3"),
        st.Page("pages/page4_something.py", title="Page4"),
    ],
}

pg = st.navigation(pages)
pg.run()
