import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Monthly Budget & Savings Planner", page_icon="💰", layout="wide")

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

DATA_FILE = "monthly_finance_perfect_data.csv"
MONTHS_FILE = "available_months_perfect.txt"

# File setup if not exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Month_Sheet", "Type", "Amount", "Category", "Description", "Date"])
    df.to_csv(DATA_FILE, index=False)

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

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h2>🧭 Navigation</h2>", unsafe_allow_html=True)
page_selection = st.sidebar.radio("Go to Page:", ["📝 Monthly Dashboard", "🔍 All Time History & Search"])

if page_selection == "📝 Monthly Dashboard":
    st.title("💰 Personal Monthly Budget Tracker")
    
    all_months = load_months()
    col_m1, col_m2 = st.columns(2)
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

    st.markdown(f"## 📊 Active Sheet: {selected_month}")
    
    # Data Calculations
    df_all = load_data()
    df_month = df_all[df_all["Month_Sheet"] == selected_month] if not df_all.empty else pd.DataFrame()
    
    income_df = df_month[df_month["Type"] == "Income (Aamdani)"] if not df_month.empty else pd.DataFrame()
    expense_df = df_month[df_month["Type"] == "Expense (Kharcha)"] if not df_month.empty else pd.DataFrame()
    savings_df = df_month[df_month["Type"] == "Savings (Bachat)"] if not df_month.empty else pd.DataFrame()

    total_income = income_df["Amount"].sum() if not income_df.empty else 0.0
    total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0.0
    total_savings = savings_df["Amount"].sum() if not savings_df.empty else 0.0
    
    # Savings bhi Clear Balance mein se minus hogi
    clear_balance = total_income - total_expense - total_savings

    # Live Balance Metrics
    st.subheader("💵 Balance Status (Is Mahine Ka)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Income", f"₹{total_income:,.2f}")
    c2.metric("📉 Total Kharcha", f"₹{total_expense:,.2f}")
    c3.metric("🏦 Alag Ki Hui Bachat", f"₹{total_savings:,.2f}")
    c4.metric("📊 Clear Balance (Bacha Paisa)", f"₹{clear_balance:,.2f}")

    st.markdown("---")

    # Entry Form
    st.subheader(f"📝 {selected_month} Mein Nayi Entry Dalein")
    entry_type = st.radio("Kya jodna hai?", ["Expense (Kharcha)", "Income (Aamdani)", "Savings (Bachat)"], horizontal=True)
    
    col_amt, col_cat = st.columns(2)
    with col_amt:
        amount = st.number_input("Amount Bharein (₹)", min_value=0.0, step=10.0, value=0.0)
    with col_cat:
        if entry_type == "Expense (Kharcha)":
            categories = ["Khana (Food)", "Rent/Makaan", "Travel/Petrol", "Shopping", "Recharge/Bills", "Others"]
        elif entry_type == "Savings (Bachat)":
            categories = ["Emergency Fund", "Future Saving", "Bank Deposit", "Others"]
        else:
            categories = ["Salary", "Business", "Freelance", "Investment", "Others"]
        category = st.selectbox("Category Chunein", categories)

    description = st.text_input("Kahan kharcha/bachat kiya ya paisa aaya? (Details)")
    date_val = st.date_input("Tareekh (Date)", datetime.now())

    if st.button("💾 ENTRY SAVE KAREIN", use_container_width=True):
        if amount > 0:
            save_data(selected_month, entry_type, amount, category, description, str(date_val))
            st.success("Entry kamyabi se save ho gayi!")
            st.rerun()
        else:
            st.error("Kripya 0 se bada amount dalein.")

    st.markdown("---")

    # --- NEW CIRCLE (PIE) CHART SECTION ---
    if not expense_df.empty:
        st.subheader("🍕 Is Mahine Kahan Kitna Kharcha Hua? (Circle Chart)")
        # Kharchon ka data Category ke hisab se group kar rahe hain
        cat_chart_data = expense_df.groupby("Category")["Amount"].sum()
        # Streamlit pie chart/circle visualization dikhane ke liye
        st.pie_chart(cat_chart_data)
        st.markdown("---")
    
    # History and Delete Feature
    st.subheader(f"📜 {selected_month} Ka Itihas (History)")
    if not df_month.empty:
        display_df = df_month[["Type", "Amount", "Category", "Description", "Date"]].copy()
        st.dataframe(display_df, use_container_width=True)
        
        with st.expander("❌ Galat Entry Mitayein / Delete Karein"):
            st.write("Upar ki list mein se jis entry ko mitana hai, uska pehla no. (Index) dekh kar niche select karein:")
            delete_index = st.selectbox("Kaun si entry delete karni hai?", df_month.index)
            if st.button("🗑️ Selected Entry Hatao", type="primary"):
                df_all = df_all.drop(delete_index)
                df_all.to_csv(DATA_FILE, index=False)
                st.success("Entry kamyabi se mita di gayi hai!")
                st.rerun()
    else:
        st.info("Is mahine mein abhi tak koi transaction save nahi hai.")

else:
    st.title("🔍 All Time Transaction History")
    df_data = load_data()
    
    if df_data.empty:
        st.info("👋 Abhi tak koi data nahi dala gaya hai.")
    else:
        search_query = st.text_input("Description se khojein:")
        filtered_df = df_data.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Description"].str.contains(search_query, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
