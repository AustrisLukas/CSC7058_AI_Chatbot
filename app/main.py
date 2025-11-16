import streamlit as st
from services import openai_service
import json

pages = {
    "Assistants": [
        st.Page("pages/pageA1_doc.py", title="DocuMind"),
        st.Page("pages/pageA2_web.py", title="WebMind"),
        st.Page("pages/pageA3_doc.py", title="DocuMind.v2"),
    ],
    "Settings": [
        st.Page("pages/pageB1_something.py", title="Page3"),
        st.Page("pages/pageB2_something.py", title="Page4"),
    ],
}

pg = st.navigation(pages)
pg.run()
