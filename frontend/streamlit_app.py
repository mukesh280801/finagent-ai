import streamlit as st
import requests

st.set_page_config(page_title="FinAgent AI", layout="wide")

st.title("💰 FinAgent AI")
st.subheader("AI-Powered Receipt Analyzer")

# 🔥 Replace with YOUR backend URL
BACKEND_URL = "https://finagent-ai-2.onrender.com/analyze"

uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)

    if st.button("Analyze Receipt"):
        with st.spinner("Processing..."):

            files = {"file": uploaded_file.getvalue()}

            try:
                response = requests.post(BACKEND_URL, files=files)

                if response.status_code == 200:
                    data = response.json()

                    st.success("Analysis Complete ✅")

                    st.write("### 🧾 Extracted Data:")
                    st.json(data)

                else:
                    st.error("Backend Error ❌")

            except Exception as e:
                st.error(f"Error: {e}")