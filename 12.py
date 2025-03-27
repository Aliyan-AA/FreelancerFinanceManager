#################################################################
# Hostel Financial Management Dashboard with Balance Sheet,     #
# Hostelite Management, Staff Payments and Dues, and               #
# Hostel Management Payments and Dues                           #
# Developed using Streamlit’s Built-in UI Components               #
# This application enables hostel owners to manage financial data,   #
# track revenue & expenses, view a dynamic balance sheet, manage     #
# hostel resident details including room assignments and payment     #
# statuses, and handle staff payments with due tracking. It also       #
# reserved space for future enhancements.                            #
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
if 'assets' not in st.session_state:
    st.session_state.assets = []       # Asset entries: Date, Description, Amount
if 'liabilities' not in st.session_state:
    st.session_state.liabilities = []  # Liability entries: Date, Description, Amount
if 'equity' not in st.session_state:
    st.session_state.equity = []         # Equity entries: Date, Description, Amount
if 'staff' not in st.session_state:
    st.session_state.staff = {}          # Staff details: key = staff name, value = {Position, Expected Payment}
if 'staff_payments' not in st.session_state:
    st.session_state.staff_payments = [] # Staff payment records: list of dicts: Date, Staff, Amount, Method

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

def add_staff(name, position, expected_payment):
    st.session_state.staff[name] = {"Position": position, "Expected Payment": expected_payment}

def add_staff_payment(date, name, amount, method):
    st.session_state.staff_payments.append({
        "Date": date,
        "Staff": name,
        "Amount": amount,
        "Method": method
    })

def compute_staff_payments():
    # Compute total paid for each staff from staff_payments records
    staff_data = {}
    for name in st.session_state.staff:
        staff_data[name] = {"Expected Payment": st.session_state.staff[name]["Expected Payment"], "Paid": 0}
    for payment in st.session_state.staff_payments:
        name = payment["Staff"]
        if name in staff_data:
            staff_data[name]["Paid"] += payment["Amount"]
    data = []
    for name, details in staff_data.items():
        expected = details["Expected Payment"]
        paid = details["Paid"]
        due = max(expected - paid, 0)
        overpaid = max(paid - expected, 0)
        data.append({
            "Staff": name,
            "Expected Payment": expected,
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

# ---------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Hostelite Management", "Staff Payments and Dues", "Hostel Management Payments and Dues", "Financial Overview", "Reports"]
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
    trends_df = compute_monthly_trends()
    fig_trends = px.line(trends_df, x="Month", y=["Revenue", "Expenses"], markers=True, title="Monthly Revenue vs Expenses")
    st.plotly_chart(fig_trends, use_container_width=True)
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
# HOSTELITE MANAGEMENT PAYMENTS AND DUES SECTION
# ---------------------------------------------------------------
elif page == "Hostel Management Payments and Dues":
    st.header("Hostel Management Payments and Dues")
    payment_details_df = compute_payment_details()
    if not payment_details_df.empty:
        st.dataframe(payment_details_df)
    else:
        st.info("No hostelite payment data available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)


# ---------------------------------------------------------------
# STAFF PAYMENTS AND DUES SECTION
# ---------------------------------------------------------------
elif page == "Staff Payments and Dues":
    st.header("Staff Payments and Dues")
    st.subheader("Add/Update Staff Information")
    with st.form("staff_form", clear_on_submit=True):
        staff_name = st.text_input("Staff Name")
        staff_position = st.text_input("Position")
        expected_payment = st.number_input("Expected Payment (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add/Update Staff"):
            st.session_state.staff[staff_name] = {"Position": staff_position, "Expected Payment": expected_payment}
            st.success(f"Staff {staff_name} added/updated successfully!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Record Staff Payment")
    with st.form("staff_payment_form", clear_on_submit=True):
        pay_date = st.date_input("Payment Date", datetime.date.today())
        staff_member = st.selectbox("Select Staff", list(st.session_state.staff.keys()) if st.session_state.staff else ["No Staff Available"])
        pay_amount = st.number_input("Payment Amount (PKR)", min_value=0.0, format="%.2f")
        pay_method = st.selectbox("Payment Method", ["Cash", "Online Transaction", "Bank Transfer"])
        if st.form_submit_button("Record Staff Payment") and staff_member != "No Staff Available":
            add_staff_payment(pay_date, staff_member, pay_amount, pay_method)
            st.success(f"Payment of PKR {pay_amount} recorded for {staff_member}!")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Staff Payment Details")
    staff_payment_df = compute_staff_payments()
    if not staff_payment_df.empty:
        st.dataframe(staff_payment_df)
    else:
        st.info("No staff payment data available.")
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


def get_hostelite_list():
    data = []
    for name, details in st.session_state.hostelites.items():
        data.append({
            "Name": name,
            "Room Number": details["Room"],
            "Monthly Rent": details["Rent"],
            "Amount Paid": details["Paid"],
            "Amount Due": max(details["Rent"] - details["Paid"], 0),
            "Payment Status": "Paid" if details["Paid"] >= details["Rent"] else "Partial" if details["Paid"] > 0 else "Unpaid"
        })
    return pd.DataFrame(data)

def process_payment(hostelite, amount, payment_date, payment_method):
    if hostelite in st.session_state.hostelites:
        add_payment(payment_date, hostelite, amount, payment_method)
        return True
    return False



# ---------------------------------------------------------------
# DASHBOARD SECTION
# ---------------------------------------------------------------

    if page == "Dashboard":
    st.header("Dashboard Overview")
    total_rev = sum([entry["Amount"] for entry in st.session_state.revenue])
    total_exp = sum([entry["Amount"] for entry in st.session_state.expenses])
    overall_balance = total_rev - total_exp
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><h4>Total Revenue</h4><h2>PKR {total_rev:,.2f}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><h4>Total Expenses</h4><h2>PKR {total_exp:,.2f}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><h4>Overall Balance</h4><h2>PKR {overall_balance:,.2f}</h2></div>", unsafe_allow_html=True)
    # Hostelite Payment Section
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Quick Payment Processing")
    payment_col1, payment_col2 = st.columns(2)
    
    with payment_col1:
        hostelite = st.selectbox("Select Hostelite", list(st.session_state.hostelites.keys()) if st.session_state.hostelites else ["No hostelites"])
        if hostelite != "No hostelites":
            amount = st.number_input("Payment Amount", min_value=0.0, value=float(st.session_state.hostelites[hostelite]["Rent"]))
            payment_date = st.date_input("Payment Date")
            payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Wallet", "Other"])
            if st.button("Process Payment"):
                if process_payment(hostelite, amount, payment_date, payment_method):
                    st.success(f"Payment of PKR {amount:,.2f} processed successfully for {hostelite}")
                else:
                    st.error("Failed to process payment")
    
    with payment_col2:
        if hostelite != "No hostelites":
            details = st.session_state.hostelites[hostelite]
            st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px;'>
                    <h4>Payment Details</h4>
                    <p><strong>Room:</strong> {details['Room']}</p>
                    <p><strong>Monthly Rent:</strong> PKR {details['Rent']:,.2f}</p>
                    <p><strong>Amount Paid:</strong> PKR {details['Paid']:,.2f}</p>
                    <p><strong>Amount Due:</strong> PKR {max(details['Rent'] - details['Paid'], 0):,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Hostelite List
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Current Hostelites")
    hostelite_df = get_hostelite_list()
    if not hostelite_df.empty:
        st.dataframe(hostelite_df, use_container_width=True)
    else:
        st.info("No hostelites registered yet")
    
   


# ---------------------------------------------------------------
# HOSTELITE MANAGEMENT SECTION
# ---------------------------------------------------------------
elif page == "Hostelite Management":
    st.header("Hostelite Management")
    
    # Add New Hostelite Form
    st.subheader("Add New Hostelite")
    with st.form("hostelite_form", clear_on_submit=True):
        hostelite_name = st.text_input("Hostelite Name")
        room_number = st.number_input("Room Number", min_value=1)
        monthly_rent = st.number_input("Monthly Rent (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add Hostelite"):
            if hostelite_name and room_number and monthly_rent:
                add_hostelite(hostelite_name, room_number, monthly_rent)
                st.success(f"Hostelite {hostelite_name} added successfully!")
            else:
                st.error("Please fill in all fields")
    
    # Display Hostelite List
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Current Hostelites")
    hostelite_df = get_hostelite_list()
    if not hostelite_df.empty:
        st.dataframe(hostelite_df, use_container_width=True)
        
        # Add payment processing section
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Process Payment")
        payment_col1, payment_col2 = st.columns(2)
        
        with payment_col1:
            selected_hostelite = st.selectbox("Select Hostelite", list(st.session_state.hostelites.keys()))
            amount = st.number_input("Payment Amount", min_value=0.0, value=float(st.session_state.hostelites[selected_hostelite]["Rent"]))
            payment_date = st.date_input("Payment Date")
            payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Wallet", "Other"])
            if st.button("Process Payment"):
                if process_payment(selected_hostelite, amount, payment_date, payment_method):
                    st.success(f"Payment of PKR {amount:,.2f} processed successfully for {selected_hostelite}")
                else:
                    st.error("Failed to process payment")
        
        with payment_col2:
            details = st.session_state.hostelites[selected_hostelite]
            st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px;'>
                    <h4>Payment Details</h4>
                    <p><strong>Room:</strong> {details['Room']}</p>
                    <p><strong>Monthly Rent:</strong> PKR {details['Rent']:,.2f}</p>
                    <p><strong>Amount Paid:</strong> PKR {details['Paid']:,.2f}</p>
                    <p><strong>Amount Due:</strong> PKR {max(details['Rent'] - details['Paid'], 0):,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hostelites registered yet")






    
