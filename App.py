import streamlit as st
import pandas as pd
import os
from datetime import datetime

# App Settings
st.set_page_config(page_title="Easy Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Personal Expense & Budget Tracker")
st.markdown("Direct entry karein aur apna monthly kharcha track karein.")

DATA_FILE = "finance_data.csv"

# File setup if not exists
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

df_data = load_data()

# Calculate totals
income_df = df_data[df_data["Type"] == "Income (Aamdani)"]
expense_df = df_data[df_data["Type"] == "Expense (Kharcha)"]

total_income = income_df["Amount"].sum()
total_expense = expense_df["Amount"].sum()
net_balance = total_income - total_expense

# --- FRONT PAGE METRICS ---
st.subheader("📊 Aapka Live Balance")
c1, c2, c3 = st.columns(3)
c1.metric("💰 Total Income", f"₹{total_income:,.2f}")
c2.metric("📉 Total Kharcha", f"₹{total_expense:,.2f}")
c3.metric("🏦 Available Balance (Bacha Paisa)", f"₹{net_balance:,.2f}")

st.markdown("---")

# --- DIRECT ENTRY FORM ON MAIN SCREEN ---
st.subheader("📝 Naya Transaction Dalein (Direct Entry)")

col_type, col_amt, col_cat = st.columns(3)
with col_type:
    entry_type = st.radio("Kya jodna hai?", ["Expense (Kharcha)", "Income (Aamdani)"], horizontal=True)

with col_amt:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, value=0.0)

with col_cat:
    if entry_type == "Expense (Kharcha)":
        categories = ["Khana (Food)", "Rent/Makaan", "Travel/Petrol", "Shopping", "Recharge/Bills", "Others"]
    else:
        categories = ["Salary", "Business", "Freelance", "Investment", "Others"]
    category = st.selectbox("Category Chunein", categories)

col_desc, col_date = st.columns([2, 1])
with col_desc:
    description = st.text_input("Kahan kharcha kiya / Kahan se paisa aaya? (Details likhein)")

with col_date:
    date_val = st.date_input("Tareekh (Date)", datetime.now())

# Save Button
if st.button("💾 Entry Save Karein", use_container_width=True):
    if amount > 0:
        save_data(entry_type, amount, category, description, str(date_val))
        st.success("Entry kamyabi se save ho gayi aur balance update ho gaya!")
        st.rerun()
    else:
        st.error("Kripya 0 se bada amount dalein.")

st.markdown("---")

# --- AVERAGES & HISTORY ---
if not df_data.empty:
    st.subheader("📈 Automatically Calculated Averages")
    avg_income = income_df["Amount"].mean() if not income_df.empty else 0
    avg_expense = expense_df["Amount"].mean() if not expense_df.empty else 0
    
    col_avg1, col_avg2 = st.columns(2)
    col_avg1.metric("📊 Average Income per entry", f"₹{avg_income:,.2f}")
    col_avg2.metric("💸 Average Kharcha per entry", f"₹{avg_expense:,.2f}")
    
    st.markdown("---")

    # History Table
    st.subheader("📜 Pura Transactions Itihas (History)")
    st.dataframe(df_data.sort_index(ascending=False), use_container_width=True)
    
    # Delete Option
    if st.button("🔴 Sabhi Data Clear Karein"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("Sabh data delete ho gaya...")
            st.rerun()
else:
    st.info("👋 Abhi tak koi data nahi dala gaya hai. Upar diye gaye form se apni pehli entry kariye!")
    
