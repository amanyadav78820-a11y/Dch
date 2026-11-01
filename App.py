import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Personal Expense & Savings Tracker")
st.markdown("Apna kharcha aur aamdani track karein aur average savings dekhein.")

DATA_FILE = "finance_data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Type", "Amount", "Category", "Description", "Date"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(type_, amount, category, desc, date):
    df = load_data()
    new_row = pd.DataFrame([[type_, amount, category, desc, date]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

st.sidebar.header("➕ Naya Entry Dalein")
entry_type = st.sidebar.selectbox("Entry Ka Type", ["Expense (Kharcha)", "Income (Aamdani)"])
amount = st.sidebar.number_input("Amount (Rupees mein)", min_value=0.0, step=100.0)

if entry_type == "Expense (Kharcha)":
    categories = ["Khana (Food)", "Rent/Makaan", "Travel/Petrol", "Shopping", "Bills/Recharge", "Others"]
else:
    categories = ["Salary", "Business", "Freelance", "Investment", "Others"]

category = st.sidebar.selectbox("Category Chunein", categories)
description = st.sidebar.text_input("Kahan kharcha kiya? (Choti details)")
date = st.sidebar.date_input("Tareekh (Date)")

if st.sidebar.button("Data Save Karein"):
    if amount > 0:
        save_data(entry_type, amount, category, description, str(date))
        st.sidebar.success("Data successfully save ho gaya!")
        st.rerun()
    else:
        st.sidebar.error("Kripya 0 se zyada amount dalein.")

df_data = load_data()

if not df_data.empty:
    income_df = df_data[df_data["Type"] == "Income (Aamdani)"]
    expense_df = df_data[df_data["Type"] == "Expense (Kharcha)"]
    
    total_income = income_df["Amount"].sum()
    total_expense = expense_df["Amount"].sum()
    total_savings = total_income - total_expense
    
    avg_income = income_df["Amount"].mean() if not income_df.empty else 0
    avg_expense = expense_df["Amount"].mean() if not expense_df.empty else 0
    
    st.subheader("📊 Aapka Financial Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Income", f"₹{total_income:,.2f}")
    col2.metric("📉 Total Kharcha (Expense)", f"₹{total_expense:,.2f}")
    col3.metric("🏦 Total Saving", f"₹{total_savings:,.2f}")
    
    st.markdown("---")
    
    st.subheader("📈 Automatically Calculated Averages")
    col4, col5 = st.columns(2)
    col4.metric("📊 Average Income per entry", f"₹{avg_income:,.2f}")
    col5.metric("💸 Average Kharcha per entry", f"₹{avg_expense:,.2f}")
    
    st.markdown("---")
    
    if not expense_df.empty:
        st.subheader("🍕 Kahan Kitna Kharcha Hua? (Category Wise)")
        cat_expense = expense_df.groupby("Category")["Amount"].sum().reset_index()
        st.dataframe(cat_expense.style.format({"Amount": "₹{:.2f}"}), use_container_width=True)
    
    st.subheader("📜 Pura Transaction Itihas (History)")
    st.dataframe(df_data, use_container_width=True)
    
    if st.button("🔴 Pura Data Delete Karein"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("Sabh data delete ho gaya...")
            st.rerun()
else:
    st.info("👋 Abhi tak koi data nahi dala gaya hai. Sidebar se apni pehli Income ya Expense ki entry kariye!")
  
