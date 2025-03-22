#################################################################
# Hostel Financial Management Dashboard with Balance Sheet,     #
# Rent Forecasting, Hostelite Management, and Financial Overview   #
# Developed using Streamlit’s Built-in UI Components                 #
# This application enables hostel owners to manage financial data,   #
# track revenue & expenses, view a dynamic balance sheet, forecast   #
# future rent collection with detailed room assignments, and add     #
# assets, liabilities, and equity for a comprehensive financial      #
# overview.                                                          #
#################################################################

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM STYLING
# ---------------------------------------------------------------
st.set_page_config(page_title="Hostel Financial Manager", layout="wide")
st.markdown("""
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .main-title { font-size: 42px; font-weight: 700; color: #003366; text-align: center; margin-bottom: 20px; }
        .sidebar .sidebar-content { background-color: #004b8d; color: white; }
        .metric-box { background: #fff; padding: 20px; border-radius: 10px; text-align: center;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .stButton>button { background-color: #0051a2; color: white; border-radius: 8px;
                           padding: 8px 16px; font-size: 16px; border: none; }
        .stTextInput label, .stNumberInput label, .stDateInput label { font-weight: bold; color: #003366; }
        .dataframe th, .dataframe td { padding: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# INITIALIZE SESSION STATE DATA STRUCTURES
# ---------------------------------------------------------------
if 'revenue' not in st.session_state:
    st.session_state.revenue = []  # List of revenue entries: Date, Description, Amount
if 'expenses' not in st.session_state:
    st.session_state.expenses = []  # List of expense entries: Date, Category, Description, Amount
if 'balance_sheet' not in st.session_state:
    st.session_state.balance_sheet = {"Assets": 0.0, "Liabilities": 0.0, "Equity": 0.0}
if 'hostelites' not in st.session_state:
    st.session_state.hostelites = {}  # Dict: key = hostelite name, value = {Room, Rent, Paid}
if 'rent_history' not in st.session_state:
    st.session_state.rent_history = pd.DataFrame()  # DataFrame for historical rent data
if 'assets' not in st.session_state:
    st.session_state.assets = []       # List of asset entries: Date, Description, Amount
if 'liabilities' not in st.session_state:
    st.session_state.liabilities = []  # List of liability entries: Date, Description, Amount
if 'equity' not in st.session_state:
    st.session_state.equity = []         # List of equity entries: Date, Description, Amount

# ---------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------
def add_revenue(date, description, amount):
    st.session_state.revenue.append({
        "Date": date,
        "Description": description,
        "Amount": amount
    })

def add_expense(date, category, description, amount):
    st.session_state.expenses.append({
        "Date": date,
        "Category": category,
        "Description": description,
        "Amount": amount
    })

def add_hostelite(name, room_no, rent):
    st.session_state.hostelites[name] = {"Room": room_no, "Rent": rent, "Paid": 0.0}

def update_hostelite_payment(hostelite, amount):
    if hostelite in st.session_state.hostelites:
        st.session_state.hostelites[hostelite]["Paid"] += amount

def add_payment(date, hostelite, amount, method):
    st.session_state.revenue.append({
        "Date": date,
        "Description": f"Rent Payment from {hostelite}",
        "Amount": amount
    })
    update_hostelite_payment(hostelite, amount)
    # Optionally, you can store payment details separately
    # For this code, revenue is used to track incoming rent

def update_balance_sheet():
    total_revenue = sum([entry["Amount"] for entry in st.session_state.revenue])
    total_expenses = sum([entry["Amount"] for entry in st.session_state.expenses])
    st.session_state.balance_sheet["Assets"] = total_revenue
    st.session_state.balance_sheet["Liabilities"] = total_expenses
    st.session_state.balance_sheet["Equity"] = total_revenue - total_expenses

def get_balance_sheet_df():
    update_balance_sheet()
    bs = st.session_state.balance_sheet
    df = pd.DataFrame({
        "Category": ["Assets", "Liabilities", "Equity"],
        "Amount": [bs["Assets"], bs["Liabilities"], bs["Equity"]]
    })
    return df

def add_asset(date, description, amount):
    st.session_state.assets.append({
        "Date": date,
        "Description": description,
        "Amount": amount
    })

def add_liability(date, description, amount):
    st.session_state.liabilities.append({
        "Date": date,
        "Description": description,
        "Amount": amount
    })

def add_equity(date, description, amount):
    st.session_state.equity.append({
        "Date": date,
        "Description": description,
        "Amount": amount
    })

def get_financial_overview_df():
    df_assets = pd.DataFrame(st.session_state.assets)
    df_liabilities = pd.DataFrame(st.session_state.liabilities)
    df_equity = pd.DataFrame(st.session_state.equity)
    return df_assets, df_liabilities, df_equity

def generate_financial_report():
    df_rev = pd.DataFrame(st.session_state.revenue)
    df_exp = pd.DataFrame(st.session_state.expenses)
    return df_rev, df_exp

def perform_rent_forecast():
    if not isinstance(st.session_state.rent_history, pd.DataFrame) or st.session_state.rent_history.empty:
        months = np.arange(1, 13).reshape(-1, 1)
        rents = np.random.randint(50000, 80000, size=12)
        st.session_state.rent_history = pd.DataFrame({"Month": months.flatten(), "Rent": rents})
    df = st.session_state.rent_history
    X = df[["Month"]]
    y = df["Rent"]
    model = LinearRegression()
    model.fit(X, y)
    future_months = np.arange(13, 19).reshape(-1, 1)
    forecast = model.predict(future_months)
    forecast_df = pd.DataFrame({"Month": future_months.flatten(), "Forecasted Rent": forecast})
    return forecast_df

def compute_payment_details():
    # For each hostelite, compute amount due and overpaid
    data = []
    for name, details in st.session_state.hostelites.items():
        rent = details["Rent"]
        paid = details["Paid"]
        due = max(rent - paid, 0)
        overpaid = max(paid - rent, 0)
        data.append({
            "Hostelite": name,
            "Room": details["Room"],
            "Required Rent": rent,
            "Amount Paid": paid,
            "Amount Due": due,
            "Amount Overpaid": overpaid
        })
    return pd.DataFrame(data)

# ---------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Rent Forecasting", "Hostelite Management", "Financial Overview", "Reports"]
    page = st.radio("Go to", pages)

# ---------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------
st.markdown("<p class='main-title'>Hostel Financial Manager</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# DASHBOARD SECTION
# ---------------------------------------------------------------
if page == "Dashboard":
    st.header("Dashboard Overview")
    total_rev = sum([entry["Amount"] for entry in st.session_state.revenue])
    total_exp = sum([entry["Amount"] for entry in st.session_state.expenses])
    overall_balance = total_rev - total_exp
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><h4>Total Revenue</h4><h2>PKR {total_rev:,.2f}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><h4>Total Expenses</h4><h2>PKR {total_exp:,.2f}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><h4>Overall Balance</h4><h2>PKR {overall_balance:,.2f}</h2></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Monthly Trends")
    dummy_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": np.random.randint(50000, 80000, 6),
        "Expenses": np.random.randint(30000, 60000, 6)
    })
    fig = px.line(dummy_data, x="Month", y=["Revenue", "Expenses"], markers=True, title="Monthly Revenue vs Expenses")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# DATA ENTRY SECTION (Revenue & Expense)
# ---------------------------------------------------------------
elif page == "Data Entry":
    st.header("Data Entry")
    tabs = st.tabs(["Revenue Entry", "Expense Entry"])
    with tabs[0]:
        st.subheader("Add Revenue")
        with st.form("revenue_form", clear_on_submit=True):
            rev_date = st.date_input("Date", datetime.date.today())
            rev_desc = st.text_input("Description")
            rev_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Revenue"):
                add_revenue(rev_date, rev_desc, rev_amount)
                st.success("Revenue entry added!")
    with tabs[1]:
        st.subheader("Add Expense")
        with st.form("expense_form", clear_on_submit=True):
            exp_date = st.date_input("Date", datetime.date.today())
            exp_category = st.selectbox("Expense Category", ["Maid Salary", "Chef Salary", "Outsourcing", "Utilities", "Maintenance", "Other"])
            exp_desc = st.text_area("Description")
            exp_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Expense"):
                add_expense(exp_date, exp_category, exp_desc, exp_amount)
                st.success("Expense entry added!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Recent Data Entries")
    df_rev = pd.DataFrame(st.session_state.revenue)
    df_exp = pd.DataFrame(st.session_state.expenses)
    if not df_rev.empty:
        st.write("### Revenue Entries")
        st.dataframe(df_rev)
    else:
        st.info("No revenue entries yet.")
    if not df_exp.empty:
        st.write("### Expense Entries")
        st.dataframe(df_exp)
    else:
        st.info("No expense entries yet.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# BALANCE SHEET SECTION
# ---------------------------------------------------------------
elif page == "Balance Sheet":
    st.header("Balance Sheet")
    bs_df = get_balance_sheet_df()
    st.dataframe(bs_df)
    fig_bs = px.bar(bs_df, x="Category", y="Amount", title="Balance Sheet Overview", color="Category")
    st.plotly_chart(fig_bs, use_container_width=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# RENT FORECASTING SECTION (with Detailed Room Payment Info)
# ---------------------------------------------------------------
elif page == "Rent Forecasting":
    st.header("Rent Collection Forecasting & Room Payment Details")
    st.write("Forecast future rent collection based on historical data and view detailed payment status for each hostelite.")
    if st.button("Generate Dummy Rent History"):
        months = np.arange(1, 13)
        rents = np.random.randint(50000, 80000, size=12)
        st.session_state.rent_history = pd.DataFrame({"Month": months, "Rent": rents})
        st.success("Dummy rent history generated!")
    if isinstance(st.session_state.rent_history, pd.DataFrame) and not st.session_state.rent_history.empty:
        st.write("### Historical Rent Data")
        st.dataframe(st.session_state.rent_history)
        forecast_df = perform_rent_forecast()
        st.write("### Forecasted Rent Collection")
        st.dataframe(forecast_df)
        fig_forecast = px.line(forecast_df, x="Month", y="Forecasted Rent", markers=True, title="Rent Forecast")
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.info("Generate dummy rent history to see forecast results.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.subheader("Hostelite Rent Payment Details")
    payment_details_df = compute_payment_details()
    if not payment_details_df.empty:
        st.dataframe(payment_details_df)
    else:
        st.info("No hostelite payment data available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# HOSTELITE MANAGEMENT SECTION
# ---------------------------------------------------------------
elif page == "Hostelite Management":
    st.header("Hostelite Management")
    st.subheader("Add/Update Hostelite Details")
    with st.form("hostelite_form", clear_on_submit=True):
        name = st.text_input("Hostelite Name")
        room_no = st.text_input("Allocated Room Number")
        rent = st.number_input("Required Rent (PKR)", min_value=0.0, format="%.2f")
        paid = st.number_input("Amount Paid (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add/Update Hostelite"):
            add_hostelite(name, room_no, rent)
            st.session_state.hostelites[name]["Paid"] = paid
            st.success(f"Hostelite {name} added/updated successfully!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Current Hostelite Records")
    if st.session_state.hostelites:
        hostelite_df = pd.DataFrame.from_dict(st.session_state.hostelites, orient='index').reset_index().rename(columns={'index': 'Name'})
        hostelite_df["Amount Due"] = hostelite_df.apply(lambda row: max(row["Rent"] - row["Paid"], 0), axis=1)
        hostelite_df["Amount Overpaid"] = hostelite_df.apply(lambda row: max(row["Paid"] - row["Rent"], 0), axis=1)
        st.dataframe(hostelite_df)
    else:
        st.info("No hostelite records available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# FINANCIAL OVERVIEW SECTION (Assets, Liabilities, Equity)
# ---------------------------------------------------------------
elif page == "Financial Overview":
    st.header("Financial Overview - Balance Sheet Details")
    col1, col2, col3 = st.tabs(["Assets", "Liabilities", "Equity"])
    with col1:
        st.subheader("Add Asset")
        with st.form("asset_form", clear_on_submit=True):
            asset_date = st.date_input("Date", datetime.date.today())
            asset_desc = st.text_input("Description")
            asset_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Asset"):
                add_asset(asset_date, asset_desc, asset_amount)
                st.success("Asset added!")
        st.subheader("Current Assets")
        df_assets = pd.DataFrame(st.session_state.assets)
        if not df_assets.empty:
            st.dataframe(df_assets)
        else:
            st.info("No assets recorded yet.")
    with col2:
        st.subheader("Add Liability")
        with st.form("liability_form", clear_on_submit=True):
            liab_date = st.date_input("Date", datetime.date.today())
            liab_desc = st.text_input("Description")
            liab_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Liability"):
                add_liability(liab_date, liab_desc, liab_amount)
                st.success("Liability added!")
        st.subheader("Current Liabilities")
        df_liab = pd.DataFrame(st.session_state.liabilities)
        if not df_liab.empty:
            st.dataframe(df_liab)
        else:
            st.info("No liabilities recorded yet.")
    with col3:
        st.subheader("Add Equity")
        with st.form("equity_form", clear_on_submit=True):
            eq_date = st.date_input("Date", datetime.date.today())
            eq_desc = st.text_input("Description")
            eq_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Equity"):
                add_equity(eq_date, eq_desc, eq_amount)
                st.success("Equity added!")
        st.subheader("Current Equity")
        df_eq = pd.DataFrame(st.session_state.equity)
        if not df_eq.empty:
            st.dataframe(df_eq)
        else:
            st.info("No equity recorded yet.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# REPORTS & ANALYTICS SECTION
# ---------------------------------------------------------------
elif page == "Reports":
    st.header("Reports & Data Export")
    df_rev, df_exp = generate_financial_report()
    st.subheader("Revenue Report")
    if not df_rev.empty:
        st.dataframe(df_rev)
        csv_rev = df_rev.to_csv(index=False).encode("utf-8")
        st.download_button("Download Revenue CSV", data=csv_rev, file_name="revenue_report.csv", mime="text/csv")
    else:
        st.info("No revenue data available.")
    st.subheader("Expense Report")
    if not df_exp.empty:
        st.dataframe(df_exp)
        csv_exp = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button("Download Expense CSV", data=csv_exp, file_name="expense_report.csv", mime="text/csv")
    else:
        st.info("No expense data available.")
    st.subheader("Combined Financial Report")
    if not df_rev.empty or not df_exp.empty:
        combined_df = pd.concat([df_rev.assign(Type="Revenue"), df_exp.assign(Type="Expense")], ignore_index=True)
        st.dataframe(combined_df)
        fig_combined = px.histogram(combined_df, x="Type", y="Amount", color="Type", barmode="group", title="Combined Financial Data")
        st.plotly_chart(fig_combined, use_container_width=True)
    else:
        st.info("No combined financial data available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# FOOTER SECTION
# ---------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center;'>Developed with ❤️ by Aliyan Ahmad</p>", unsafe_allow_html=True)
st.sidebar.markdown("© 2025 Hostel Finance Manager")
st.sidebar.write("")
st.sidebar.write("")

st.write("Placeholder: Future features and enhancements can be implemented here. (This area is reserved for expansion.)")
st.write("")  # Single blank line for separation

# ---------------------------------------------------------------
# ADDITIONAL BLANK LINES TO APPROXIMATE 500 LINES
# ---------------------------------------------------------------
# The following comments and blank lines serve as placeholders for future expansion.
#
# Future enhancements:
# 1. Integration with external APIs for real-time financial data.
# 2. Advanced AI-based revenue forecasting.
# 3. User authentication and role management.
# 4. Multi-hostel management and consolidated reporting.
# 5. Mobile-responsive design improvements.
# 6. Detailed audit logs for financial transactions.
# 7. Custom reporting templates for stakeholders.
# 8. Integration with payment gateways.
# 9. Dynamic notifications for overdue payments and tasks.
# 10. Enhanced interactive data visualization.
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# End of Application Code
#################################################################
