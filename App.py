import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Monthly Budget Planner", page_icon="💰", layout="wide")

# CSS to make text and input boxes BIGGER for easy mobile typing
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        font-size: 20px !important;
        height: 55px !important;
    }
    .stRadio div role {
        font-size: 20px !important;
    }
    h1 { font-size: 40px !important; }
    h2 { font-size: 32px !important; }
    h3 { font-size: 26px !important; }
    div[data-testid="stMetricValue"] {
        font-size: 35px !important;
    }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "monthly_finance_data.csv"
MONTHS_FILE = "available_months.txt"

# File setup if not exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Month_Sheet", "Type", "Amount", "Category", "Description", "Date"])
    df.to_csv(DATA_FILE, index=False)

# Available months load aur save karne ke functions
def load_months():
    current_month_str = datetime.now().strftime("%B-%Y")
    if os.path.exists(MONTHS_FILE):
        with open(MONTHS_FILE, "r") as f:
            months = [line.strip() for line in f.readlines() if line.strip()]
        if current_month_str not in months:
            months.append(current_month_str)
        return months
    return [current_month_str]

def add_new_month(month_name):
    months = load_months()
    if month_name not in months:
        with open(MONTHS_FILE, "a") as f:
            f.write(month_name + "\n")
        return True
    return False

def load_data():
    df = pd.read_csv(DATA_FILE)
    if not df.empty:
        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce')
    return df

def save_data(month_sheet, type_, amount, category, desc, date):
    df = load_data()
    new_row = pd.DataFrame([[month_sheet, type_, amount, category, desc, date]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- APP NAVIGATION ---
st.sidebar.markdown("## 🧭 Navigation Menu")
page_selection = st.sidebar.radio("Go to Page:", ["📝 Monthly Dashboard", "🔍 All Time History & Search"])

# --- PAGE 1: MONTHLY DASHBOARD ---
if page_selection == "📝 Monthly Dashboard":
    st.title("💰 Personal Monthly Budget & Sheets")
    
    # Month Selector & New Month Add Option
    all_months = load_months()
    
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        selected_month = st.selectbox("📅 Kis Mahine Ka Hisab Dekhna Hai?", all_months, index=len(all_months)-1)
    
    with col_m2:
        st.markdown("🆕 **Naya Mahina Shuru Karein**")
        with st.popover("➕ Naya Month Page"):
            new_month_input = st.text_input("Month-Year likhein (e.g. Dec-2026):")
            if st.button("Create Sheet"):
                if new_month_input:
                    if add_new_month(new_month_input.strip()):
                        st.success(f"{new_month_input} ki sheet ban gayi!")
                        st.rerun()
                    else:
                        st.warning("Yeh month pehle se maujood hai.")
                else:
                    st.error("Kripya naam likhein.")

    st.markdown(f"## 📊 Active Sheet: {selected_month}")
    
    # Current selected month ka data filter karna
    df_all = load_data()
    df_month = df_all[df_all["Month_Sheet"] == selected_month] if not df_all.empty else pd.DataFrame()
    
    income_df = df_month[df_month["Type"] == "Income (Aamdani)"] if not df_month.empty else pd.DataFrame()
    expense_df = df_month[df_month["Type"] == "Expense (Kharcha)"] if not df_month.empty else pd.DataFrame()

    total_income = income_df["Amount"].sum() if not income_df.empty else 0.0
    total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0.0
    clear_balance = total_income - total_expense

    # Live Balance Metrics for Selected Month
    st.subheader("💵 Balance Status (Is Mahine Ka)")
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Income", f"₹{total_income:,.2f}")
    c2.metric("📉 Total Kharcha", f"₹{total_expense:,.2f}")
    c3.metric("🏦 Clear Balance", f"₹{clear_balance:,.2f}")

    st.markdown("---")

    # Direct Entry Form
    st.subheader(f"📝 {selected_month} Mein Nayi Entry Dalein")
    entry_type = st.radio("Kya jodna hai?", ["Expense (Kharcha)", "Income (Aamdani)"], horizontal=True)
    
    col_amt, col_cat = st.columns(2)
    with col_amt:
        amount = st.number_input("Amount Bharein (₹)", min_value=0.0, step=10.0, value=0.0)
    with col_cat:
        if entry_type == "Expense (Kharcha)":
            categories = ["Khana (Food)", "Rent/Makaan", "Travel/Petrol", "Shopping", "Recharge/Bills", "Others"]
        else:
            categories = ["Salary", "Business", "Freelance", "Investment", "Others"]
        category = st.selectbox("Category Chunein", categories)

    description = st.text_input("Kahan kharcha kiya / Kahan se paisa aaya? (Details likhein)")
    date_val = st.date_input("Tareekh (Date)", datetime.now())

    if st.button("💾 ENTRY SAVE KAREIN", use_container_width=True):
        if amount > 0:
            save_data(selected_month, entry_type, amount, category, description, str(date_val))
            st.success(f"Entry kamyabi se {selected_month} ki sheet mein save ho gayi!")
            st.rerun()
        else:
            st.error("Kripya 0 se bada amount dalein.")

    st.markdown("---")
    
    # Is Mahine ki History List
    st.subheader(f"📜 {selected_month} Ka Kharcha Itihas (History)")
    if not df_month.empty:
        st.dataframe(df_month[["Date", "Type", "Amount", "Category", "Description"]].sort_index(ascending=False), use_container_width=True)
        
        # Charts for selected month
        if not expense_df.empty:
            st.markdown("#### 🍕 Is Mahine Kahan Kitna Kharcha Hua?")
            cat_data = expense_df.groupby("Category")["Amount"].sum()
            st.pie_chart(cat_data)
    else:
        st.info("Is mahine mein abhi tak koi transaction save nahi hai.")

# --- PAGE 2: ALL TIME HISTORY & SEARCH ---
else:
    st.title("🔍 All Time Transaction History")
    df_data = load_data()
    
    if df_data.empty:
        st.info("👋 Abhi tak koi data nahi dala gaya hai.")
    else:
        st.subheader("🔎 Sabhi Mahino Ka Data Filter & Search")
        search_query = st.text_input("Kahan kharcha kiya (Description) se search karein:")
        
        filtered_df = df_data.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Description"].str.contains(search_query, case=False, na=False)]
            
        st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
        
        if st.button("🔴 Sabhi Mahino Ka Data Clear Karein", use_container_width=True):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            if os.path.exists(MONTHS_FILE):
                os.remove(MONTHS_FILE)
            st.success("Sabh data kamyabi se delete ho gaya...")
            st.rerun()
    
