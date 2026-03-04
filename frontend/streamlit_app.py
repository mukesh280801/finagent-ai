import streamlit as st

st.set_page_config(page_title="FinAgent AI", layout="wide")

st.title("💰 FinAgent AI")
st.subheader("AI-Powered Receipt Analyzer")

uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
    st.success("Receipt uploaded successfully!")