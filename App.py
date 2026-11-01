import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

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
        df["Amount"] = df["Amount"].fillna(0.0)
    return df

def save_data(month_sheet, type_, amount, category, desc, date):
    df = load_data()
    new_row = pd.DataFrame([[month_sheet, type_, amount, category, desc, date]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- LANGUAGE DICTIONARY ---
lang_dict = {
    "English": {
        "nav_title": "🧭 Navigation",
        "nav_dash": "📝 Monthly Dashboard",
        "nav_hist": "🔍 All Time History & Search",
        "title": "💰 Personal Monthly Budget Tracker",
        "select_month": "📅 Which Month's Account to View?",
        "new_month": "🆕 Start New Month",
        "new_month_btn": "➕ New Month Page",
        "new_month_input": "Type Month-Year (e.g. Dec-2026):",
        "create_btn": "Create Sheet",
        "active_sheet": "📊 Active Sheet:",
        "bal_status": "💵 Balance Status (This Month)",
        "total_inc": "💰 Total Income",
        "total_exp": "📉 Total Expense",
        "total_sav": "🏦 Set Aside Savings",
        "clear_bal": "📊 Clear Balance (Available to spend)",
        "new_entry": "📝 Add New Entry in",
        "q_add": "What to add?",
        "exp": "Expense (Kharcha)",
        "inc": "Income (Aamdani)",
        "sav": "Savings (Bachat)",
        "amt_label": "Enter Amount (₹)",
        "cat_label": "Choose Category",
        "details_label": "Where did you spend/save or source? (Details)",
        "date_label": "Date",
        "save_btn": "💾 SAVE ENTRY",
        "chart_title": "🍕 Where was the money spent? (Colorful Pie Chart)",
        "hist_title": "📜 History of this Month",
        "del_title": "❌ Erase / Delete Wrong Entry",
        "del_desc": "Look at the index number from the list above and select it below to delete:",
        "del_select": "Which entry to delete?",
        "del_btn": "🗑️ Remove Selected Entry",
        "no_data": "No transactions saved in this month yet.",
        "search_label": "Search by Description:",
        "all_hist_title": "🔍 All Time Transaction History",
        "all_no_data": "👋 No data entered yet."
    },
    "Hindi": {
        "nav_title": "🧭 नेविगेशन मेनू",
        "nav_dash": "📝 मंथली डैशबोर्ड",
        "nav_hist": "🔍 कुल इतिहास और खोज",
        "title": "💰 पर्सनल मंथली बजट ट्रैकर",
        "select_month": "📅 किस महीने का हिसाब देखना है?",
        "new_month": "🆕 नया महीना शुरू करें",
        "new_month_btn": "➕ नया महीना पेज",
        "new_month_input": "महीना-साल लिखें (जैसे Dec-2026):",
        "create_btn": "शीट बनाएं",
        "active_sheet": "📊 एक्टिव शीट:",
        "bal_status": "💵 बैलेंस स्टेटस (इस महीने का)",
        "total_inc": "💰 कुल आमदनी (Income)",
        "total_exp": "📉 कुल खर्चा (Expense)",
        "total_sav": "🏦 अलग की हुई बचत",
        "clear_bal": "📊 क्लियर बैलेंस (खर्च के लिए बचा)",
        "new_entry": "📝 नयी एंट्री डालें -",
        "q_add": "क्या जोड़ना है?",
        "exp": "Expense (खर्चा)",
        "inc": "Income (आमदनी)",
        "sav": "Savings (बचत)",
        "amt_label": "अमाउंट भरें (₹)",
        "cat_label": "कैटेगरी चुनें",
        "details_label": "कहाँ खर्चा/बचत किया या पैसा आया? (विवरण)",
        "date_label": "तारीख (Date)",
        "save_btn": "💾 एंट्री सेव करें",
        "chart_title": "🍕 इस महीने कहाँ कितना खर्चा हुआ? (कलरफुल चार्ट)",
        "hist_title": "📜 इस महीने का इतिहास (History)",
        "del_title": "❌ गलत एंट्री मिटाएं / डिलीट करें",
        "del_desc": "ऊपर की लिस्ट में से जिस एंट्री को मिटाना है, उसका पहला नंबर (Index) देखकर नीचे चुनें:",
        "del_select": "कौन सी एंट्री डिलीट करनी है?",
        "del_btn": "🗑️ चुनी हुई एंट्री हटाओ",
        "no_data": "इस महीने में अभी तक कोई ट्रांजैक्शन सेव नहीं है।",
        "search_label": "विवरण (Description) से खोजें:",
        "all_hist_title": "🔍 सभी महीनों का ट्रांजैक्शन इतिहास",
        "all_no_data": "👋 अभी तक कोई डाटा नहीं डाला गया है।"
    }
}

# --- TOP LANGUAGE SELECTOR ---
selected_lang = st.selectbox("🌐 Choose Language / भाषा चुनें", ["English", "Hindi"], index=1)
t = lang_dict[selected_lang]

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h2>{t['nav_title']}</h2>", unsafe_allow_html=True)
page_selection = st.sidebar.radio("Go to Page:", [t["nav_dash"], t["nav_hist"]])

if page_selection == t["nav_dash"]:
    st.title(t["title"])
    
    all_months = load_months()
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        selected_month = st.selectbox(t["select_month"], all_months, index=len(all_months)-1)
    with col_m2:
        st.markdown(t["new_month"])
        with st.popover(t["new_month_btn"]):
            new_month_input = st.text_input(t["new_month_input"])
            if st.button(t["create_btn"]):
                if new_month_input:
                    if add_new_month(new_month_input.strip()):
                        st.success(f"{new_month_input} added!")
                        st.rerun()

    st.markdown(f"## {t['active_sheet']} {selected_month}")
    
    # Data Calculations
    df_all = load_data()
    df_month = df_all[df_all["Month_Sheet"] == selected_month] if not df_all.empty else pd.DataFrame()
    
    income_df = df_month[df_month["Type"] == "Income (Aamdani)"] if not df_month.empty else pd.DataFrame()
    expense_df = df_month[df_month["Type"] == "Expense (Kharcha)"] if not df_month.empty else pd.DataFrame()
    savings_df = df_month[df_month["Type"] == "Savings (Bachat)"] if not df_month.empty else pd.DataFrame()

    total_income = income_df["Amount"].sum() if not income_df.empty else 0.0
    total_expense = expense_df["Amount"].sum() if not expense_df.empty else 0.0
    total_savings = savings_df["Amount"].sum() if not savings_df.empty else 0.0
    
    clear_balance = total_income - total_expense - total_savings

    # Live Balance Metrics
    st.subheader(t["bal_status"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t["total_inc"], f"₹{total_income:,.2f}")
    c2.metric(t["total_exp"], f"₹{total_expense:,.2f}")
    c3.metric(t["total_sav"], f"₹{total_savings:,.2f}")
    c4.metric(t["clear_bal"], f"₹{clear_balance:,.2f}")

    st.markdown("---")

    # Entry Form
    st.subheader(f"{t['new_entry']} {selected_month}")
    
    type_map = {t["exp"]: "Expense (Kharcha)", t["inc"]: "Income (Aamdani)", t["sav"]: "Savings (Bachat)"}
    chosen_radio = st.radio(t["q_add"], [t["exp"], t["inc"], t["sav"]], horizontal=True)
    entry_type = type_map[chosen_radio]
    
    col_amt, col_cat = st.columns(2)
    with col_amt:
        amount = st.number_input(t["amt_label"], min_value=0.0, step=10.0, value=0.0)
    with col_cat:
        if entry_type == "Expense (Kharcha)":
            categories = ["Khana (Food)", "Rent/Makaan", "Travel/Petrol", "Shopping", "Recharge/Bills", "Others"]
        elif entry_type == "Savings (Bachat)":
            categories = ["Emergency Fund", "Future Saving", "Bank Deposit", "Others"]
        else:
            categories = ["Salary", "Business", "Freelance", "Investment", "Others"]
        category = st.selectbox(t["cat_label"], categories)

    description = st.text_input(t["details_label"])
    date_val = st.date_input(t["date_label"], datetime.now())

    if st.button(t["save_btn"], use_container_width=True):
        if amount > 0:
            save_data(selected_month, entry_type, amount, category, description, str(date_val))
            st.success("Saved successfully!")
            st.rerun()

    st.markdown("---")

    # --- COLORFUL PLOTLY PIE CHART ---
    if not expense_df.empty and expense_df["Amount"].sum() > 0:
        st.subheader(t["chart_title"])
        cat_chart_data = expense_df.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(cat_chart_data, values='Amount', names='Category', 
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     hole=0.1)
        fig.update_traces(textposition='inside', textinfo='percent+label', font_size=16)
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

    # History and Delete Feature
    st.subheader(t["hist_title"])
    if not df_month.empty:
        display_df = df_month[["Type", "Amount", "Category", "Description", "Date"]].copy()
        st.dataframe(display_df, use_container_width=True)
        
        with st.expander(t["del_title"]):
            st.write(t["del_desc"])
            delete_index = st.selectbox(t["del_select"], df_month.index)
            if st.button(t["del_btn"], type="primary"):
                df_all = df_all.drop(delete_index)
                df_all.to_csv(DATA_FILE, index=False)
                st.success("Deleted!")
                st.rerun()
    else:
        st.info(t["no_data"])

else:
    st.title(t["all_hist_title"])
    df_data = load_data()
    
    if df_data.empty:
        st.info(t["all_no_data"])
    else:
        search_query = st.text_input(t["search_label"])
        filtered_df = df_data.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Description"].str.contains(search_query, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
    
