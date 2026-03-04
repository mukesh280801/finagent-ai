import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://finagent-ai-bjd3.onrender.com"

st.set_page_config(page_title="FinAgent AI", layout="wide")

st.title("💰 FinAgent AI - Smart Expense Tracker")

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Navigate",
    ["Upload Receipt", "Analytics", "Weekly Report", "AI Advisor"]
)

# ----------------------------
# 1️⃣ Upload Receipt
# ----------------------------
if page == "Upload Receipt":
    st.header("📤 Upload Receipt")

    uploaded_file = st.file_uploader("Upload receipt image or PDF")

    if uploaded_file:
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{BASE_URL}/upload", files=files)

        if response.status_code == 200:
            st.success("File uploaded successfully!")
            st.json(response.json())
        else:
            st.error("Upload failed.")

# ----------------------------
# 2️⃣ Analytics
# ----------------------------
elif page == "Analytics":
    st.header("📊 Analytics Dashboard")

    if st.button("Load Monthly Summary"):
        response = requests.get(f"{BASE_URL}/advisor/2026-02")

        if response.status_code == 200:
            data = response.json()

            # Metrics Row
            col1, col2, col3 = st.columns(3)

            col1.metric("Total Spend", f"₹{data['total']}")
            col2.metric("Top Category", data["category_totals"][0]["category"])
            col3.metric("Top Merchant", data["top_merchants"][0]["merchant"])

            # Category Chart
            st.subheader("Category Breakdown")
            df = pd.DataFrame(data["category_totals"])
            st.bar_chart(df.set_index("category"))

        else:
            st.error("Failed to load analytics.")

# ----------------------------
# 3️⃣ Weekly Report
# ----------------------------
elif page == "Weekly Report":
    st.header("📅 Weekly Report")

    start_date = st.text_input("Start Date (YYYY-MM-DD)", "2026-02-01")
    end_date = st.text_input("End Date (YYYY-MM-DD)", "2026-02-28")

    if st.button("Generate Report"):
        response = requests.get(
            f"{BASE_URL}/report",
            params={"start": start_date, "end": end_date}
        )

        if response.status_code == 200:
            data = response.json()

            st.metric("Total Spend", f"₹{data['total']}")

            st.subheader("Top Merchant")
            st.write(data["top_merchants"])

            st.subheader("Insights")
            for insight in data["insights"]:
                st.write(f"• {insight}")

        else:
            st.error("Failed to generate report.")

# ----------------------------
# 4️⃣ AI Advisor
# ----------------------------
elif page == "AI Advisor":
    st.header("🤖 AI Financial Advisor")

    month = st.text_input("Enter Month (YYYY-MM)", "2026-02")

    if st.button("Get Advice"):
        response = requests.get(f"{BASE_URL}/advisor/{month}")

        if response.status_code == 200:
            data = response.json()

            st.subheader("📈 Insights")
            for insight in data["insights"]:
                st.write(f"• {insight}")

            st.subheader("💡 Suggestions")
            for suggestion in data["suggestions"]:
                st.write(f"• {suggestion}")

        else:
            st.error("Failed to get advice.")