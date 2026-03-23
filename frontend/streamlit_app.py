import streamlit as st
import requests

st.set_page_config(page_title="FinAgent AI", layout="wide")

st.title("💰 FinAgent AI")
st.subheader("AI-Powered Receipt Analyzer")

# 👉 Replace with your BACKEND URL
BACKEND_URL = "https://finagent-ai-2.onrender.com/upload"

uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
    st.success("Receipt uploaded successfully!")

    if st.button("Analyze Receipt"):
        files = {"file": uploaded_file.getvalue()}

        try:
            response = requests.post(BACKEND_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                st.write("### 📊 Result:")
                st.json(result)
            else:
                st.error(f"Error: {response.text}")

        except Exception as e:
            st.error(f"Backend connection failed: {e}")