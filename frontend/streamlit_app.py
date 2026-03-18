import streamlit as st
import requests

st.set_page_config(page_title="FinAgent AI", layout="wide")

st.title("💰 FinAgent AI")
st.subheader("AI-Powered Receipt Analyzer")

# 🔥 IMPORTANT — Put your REAL backend URL here
BACKEND_URL = "https://finagent-backend.onrender.com/analyze"

uploaded_file = st.file_uploader(
    "Upload a receipt image", 
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)

    with st.spinner("Analyzing receipt..."):
        try:
            response = requests.post(
                BACKEND_URL,
                files={"file": uploaded_file.getvalue()}
            )

            if response.status_code == 200:
                st.success("Analysis Complete!")
                result = response.json()
                st.json(result)
            else:
                st.error("Backend error. Please check API.")

        except Exception as e:
            st.error(f"Connection error: {e}")