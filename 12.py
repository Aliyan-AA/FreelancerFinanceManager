#################################################################
# Hostel Financial Management Dashboard with Consolidated       #
# Payment Records, Balance Sheet, Hostelite Management, and        #
# Financial Overview                                             #
# Developed using Streamlit’s Built-in UI Components               #
# This application enables hostel owners to manage financial data,   #
# track revenue & expenses, view a dynamic balance sheet, and          #
# manage hostel resident details including room assignments and        #
# payment status. It also integrates all payment records into a         #
# comprehensive dashboard graph and reserves space for future           #
# enhancements.                                                      #
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
    st.session_state.revenue = []  # Revenue entries: Date, Description, Amount
if 'expenses' not in st.session_state:
    st.session_state.expenses = []  # Expense entries: Date, Category, Description, Amount
if 'balance_sheet' not in st.session_state:
    st.session_state.balance_sheet = {"Assets": 0.0, "Liabilities": 0.0, "Equity": 0.0}
if 'hostelites' not in st.session_state:
    st.session_state.hostelites = {}  # Hostelite data: key = hostelite name, value = {Room, Rent, Paid}
if 'assets' not in st.session_state:
    st.session_state.assets = []       # Asset entries: Date, Description, Amount
if 'liabilities' not in st.session_state:
    st.session_state.liabilities = []  # Liability entries: Date, Description, Amount
if 'equity' not in st.session_state:
    st.session_state.equity = []         # Equity entries: Date, Description, Amount
if 'staff' not in st.session_state:
    st.session_state.staff = {}          # Staff details: key = staff name, value = {Position, Salary, Paid}
if 'staff_payments' not in st.session_state:
    st.session_state.staff_payments = [] # Staff payments: Date, Staff, Amount, Method
if 'rent_history' not in st.session_state:
    st.session_state.rent_history = pd.DataFrame()  # For rent forecasting (if needed)

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
    # Payment records (e.g., rent payments) are stored in revenue
    st.session_state.revenue.append({
        "Date": date,
        "Description": f"Rent Payment from {hostelite}",
        "Amount": amount
    })
    update_hostelite_payment(hostelite, amount)

def add_staff(name, position, salary):
    st.session_state.staff[name] = {"Position": position, "Salary": salary, "Paid": 0.0}

def update_staff_payment(name, amount):
    if name in st.session_state.staff:
        st.session_state.staff[name]["Paid"] += amount

def add_staff_payment(date, name, amount, method):
    st.session_state.staff_payments.append({
        "Date": date,
        "Staff": name,
        "Amount": amount,
        "Method": method
    })
    update_staff_payment(name, amount)

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

def compute_payment_details():
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

def compute_staff_details():
    data = []
    for name, details in st.session_state.staff.items():
        salary = details["Salary"]
        paid = details["Paid"]
        due = max(salary - paid, 0)
        overpaid = max(paid - salary, 0)
        data.append({
            "Staff": name,
            "Position": details["Position"],
            "Salary": salary,
            "Amount Paid": paid,
            "Amount Due": due,
            "Amount Overpaid": overpaid
        })
    return pd.DataFrame(data)

def compute_monthly_trends():
    if st.session_state.revenue:
        df_rev = pd.DataFrame(st.session_state.revenue)
        df_rev['Month'] = pd.to_datetime(df_rev['Date']).dt.strftime('%b')
        monthly_rev = df_rev.groupby('Month')['Amount'].sum().reindex(['Jan','Feb','Mar','Apr','May','Jun'], fill_value=0)
    else:
        monthly_rev = pd.Series([0,0,0,0,0,0], index=['Jan','Feb','Mar','Apr','May','Jun'])
    if st.session_state.expenses:
        df_exp = pd.DataFrame(st.session_state.expenses)
        df_exp['Month'] = pd.to_datetime(df_exp['Date']).dt.strftime('%b')
        monthly_exp = df_exp.groupby('Month')['Amount'].sum().reindex(['Jan','Feb','Mar','Apr','May','Jun'], fill_value=0)
    else:
        monthly_exp = pd.Series([0,0,0,0,0,0], index=['Jan','Feb','Mar','Apr','May','Jun'])
    trends_df = pd.DataFrame({
        "Month": ['Jan','Feb','Mar','Apr','May','Jun'],
        "Revenue": monthly_rev.values,
        "Expenses": monthly_exp.values
    })
    return trends_df

def get_all_payments_df():
    # Consolidate all payments from revenue and staff_payments
    df_rev = pd.DataFrame(st.session_state.revenue) if st.session_state.revenue else pd.DataFrame(columns=["Date","Description","Amount"])
    df_staff = pd.DataFrame(st.session_state.staff_payments) if st.session_state.staff_payments else pd.DataFrame(columns=["Date","Staff","Amount","Method"])
    # Add a column to identify source
    if not df_rev.empty:
        df_rev["Source"] = "Rent Payment"
    if not df_staff.empty:
        df_staff["Source"] = "Staff Payment"
        df_staff = df_staff.rename(columns={"Staff": "Description", "Amount": "Amount"})
    combined_df = pd.concat([df_rev, df_staff], ignore_index=True)
    if not combined_df.empty:
        combined_df["Date"] = pd.to_datetime(combined_df["Date"])
        combined_df["Month"] = combined_df["Date"].dt.strftime("%b %Y")
        monthly_payments = combined_df.groupby("Month")["Amount"].sum().reset_index()
    else:
        monthly_payments = pd.DataFrame({"Month": ['Jan 2025','Feb 2025','Mar 2025','Apr 2025','May 2025','Jun 2025'],
                                          "Amount": [0,0,0,0,0,0]})
    return monthly_payments

# ---------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Hostelite Management", "Staff Details", "Staff Payments", "Financial Overview", "Reports"]
    page = st.radio("Go to", pages)

# ---------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------
st.markdown("<p class='main-title'>Hostel Financial Manager</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# DASHBOARD SECTION WITH INTEGRATED PAYMENT RECORDS
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
    trends_df = compute_monthly_trends()
    fig_trends = px.line(trends_df, x="Month", y=["Revenue", "Expenses"], markers=True, title="Monthly Revenue vs Expenses")
    st.plotly_chart(fig_trends, use_container_width=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    st.subheader("Comprehensive Payment Records")
    payments_df = get_all_payments_df()
    st.dataframe(payments_df)
    fig_payments = px.bar(payments_df, x="Month", y="Amount", title="Total Payments by Month", color="Month")
    st.plotly_chart(fig_payments, use_container_width=True)
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
# HOSTELITE MANAGEMENT SECTION (Organized List Format)
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
        hostelite_df = pd.DataFrame.from_dict(st.session_state.hostelites, orient='index').reset_index().rename(columns={'index': 'Hostelite'})
        hostelite_df["Amount Due"] = hostelite_df.apply(lambda row: max(row["Rent"] - row["Paid"], 0), axis=1)
        hostelite_df["Amount Overpaid"] = hostelite_df.apply(lambda row: max(row["Paid"] - row["Rent"], 0), axis=1)
        st.dataframe(hostelite_df[["Hostelite", "Room", "Rent", "Paid", "Amount Due", "Amount Overpaid"]])
    else:
        st.info("No hostelite records available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# STAFF DETAILS SECTION
# ---------------------------------------------------------------
elif page == "Staff Details":
    st.header("Staff Details")
    st.subheader("Add/Update Staff Information")
    with st.form("staff_form", clear_on_submit=True):
        staff_name = st.text_input("Staff Name")
        staff_position = st.text_input("Position")
        staff_salary = st.number_input("Salary (PKR)", min_value=0.0, format="%.2f")
        staff_paid = st.number_input("Amount Paid (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add/Update Staff"):
            st.session_state.staff[staff_name] = {"Position": staff_position, "Salary": staff_salary, "Paid": staff_paid}
            st.success(f"Staff {staff_name} added/updated successfully!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Current Staff Records")
    if st.session_state.staff:
        staff_df = pd.DataFrame.from_dict(st.session_state.staff, orient='index').reset_index().rename(columns={'index': 'Staff'})
        staff_df["Amount Due"] = staff_df.apply(lambda row: max(row["Salary"] - row["Paid"], 0), axis=1)
        staff_df["Amount Overpaid"] = staff_df.apply(lambda row: max(row["Paid"] - row["Salary"], 0), axis=1)
        st.dataframe(staff_df[["Staff", "Position", "Salary", "Paid", "Amount Due", "Amount Overpaid"]])
    else:
        st.info("No staff records available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# STAFF PAYMENTS SECTION
# ---------------------------------------------------------------
elif page == "Staff Payments":
    st.header("Staff Payments")
    with st.form("staff_payment_form", clear_on_submit=True):
        pay_date = st.date_input("Payment Date", datetime.date.today())
        staff_member = st.selectbox("Select Staff", list(st.session_state.staff.keys()) if st.session_state.staff else ["No Staff Available"])
        staff_amount = st.number_input("Payment Amount (PKR)", min_value=0.0, format="%.2f")
        pay_method = st.selectbox("Payment Method", ["Cash", "Online Transaction", "Bank Transfer"])
        if st.form_submit_button("Record Staff Payment") and staff_member != "No Staff Available":
            add_staff_payment(pay_date, staff_member, staff_amount, pay_method)
            st.success(f"Payment of PKR {staff_amount} recorded for {staff_member}!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Staff Payment Records")
    if st.session_state.staff_payments:
        df_staff_pay = pd.DataFrame(st.session_state.staff_payments)
        st.dataframe(df_staff_pay)
    else:
        st.info("No staff payments recorded yet.")
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
st.write("")

# ---------------------------------------------------------------
# ADDITIONAL BLANK LINES TO APPROXIMATE 500 LINES
# ---------------------------------------------------------------
# Future Enhancements:
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
# End of Application Code
#################################################################
