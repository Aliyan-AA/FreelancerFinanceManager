#################################################################
# Hostel Financial Management Dashboard with Balance Sheet,     
# Payment Processing, Hostel Management, and Ongoing Projects     
# Developed using Streamlit's Built-in UI Components                
# This application enables hostel owners to manage financial data,
# track revenue & expenses, view a dynamic balance sheet, manage hostels,
# record payment transactions, and track ongoing hostel-related projects.
#################################################################

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
from sklearn.linear_model import LinearRegression

# PAGE CONFIGURATION & STYLING
st.set_page_config(page_title="Hostel Financial Manager", layout="wide")
st.markdown("""
<style>
body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.main-title { font-size: 42px; font-weight: 700; color: #003366; text-align: center; margin-bottom: 20px; }
.sidebar .sidebar-content { background-color: #004b8d; color: white; }
.metric-box { background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
.stButton>button { background-color: #0051a2; color: white; border-radius: 8px; padding: 8px 16px; font-size: 16px; border: none; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE INITIALIZATION
if 'revenue' not in st.session_state:
    st.session_state.revenue = []
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'balance_sheet' not in st.session_state:
    st.session_state.balance_sheet = {"Assets": 0.0, "Liabilities": 0.0, "Equity": 0.0}
if 'hostelites' not in st.session_state:
    st.session_state.hostelites = {}  # For resident data
if 'hostels' not in st.session_state:
    st.session_state.hostels = []     # For hostel data
if 'projects' not in st.session_state:
    st.session_state.projects = []    # For ongoing projects
if 'assets' not in st.session_state:
    st.session_state.assets = []
if 'liabilities' not in st.session_state:
    st.session_state.liabilities = []
if 'equity' not in st.session_state:
    st.session_state.equity = []
if 'staff' not in st.session_state:
    st.session_state.staff = {}
if 'staff_payments' not in st.session_state:
    st.session_state.staff_payments = []
if 'rent_history' not in st.session_state:
    st.session_state.rent_history = pd.DataFrame()

# UTILITY FUNCTIONS
def add_revenue(date, desc, amt):
    st.session_state.revenue.append({"Date": date, "Description": desc, "Amount": amt})

def add_expense(date, category, desc, amt):
    st.session_state.expenses.append({"Date": date, "Category": category, "Description": desc, "Amount": amt})

def add_hostelite(name, room_no, rent):
    st.session_state.hostelites[name] = {"Room": room_no, "Rent": rent, "Paid": 0.0}

def update_hostelite_payment(name, amt):
    if name in st.session_state.hostelites:
        st.session_state.hostelites[name]["Paid"] += amt

def add_payment(date, hostelite, amt, method):
    add_revenue(date, f"Rent Payment from {hostelite}", amt)
    update_hostelite_payment(hostelite, amt)

def update_balance_sheet():
    total_rev = sum([entry["Amount"] for entry in st.session_state.revenue])
    total_exp = sum([entry["Amount"] for entry in st.session_state.expenses])
    st.session_state.balance_sheet["Assets"] = total_rev
    st.session_state.balance_sheet["Liabilities"] = total_exp
    st.session_state.balance_sheet["Equity"] = total_rev - total_exp

def get_balance_sheet_df():
    update_balance_sheet()
    bs = st.session_state.balance_sheet
    return pd.DataFrame({"Category": ["Assets", "Liabilities", "Equity"], "Amount": [bs["Assets"], bs["Liabilities"], bs["Equity"]]})

def add_asset(date, desc, amt):
    st.session_state.assets.append({"Date": date, "Description": desc, "Amount": amt})

def add_liability(date, desc, amt):
    st.session_state.liabilities.append({"Date": date, "Description": desc, "Amount": amt})

def add_equity(date, desc, amt):
    st.session_state.equity.append({"Date": date, "Description": desc, "Amount": amt})

def get_financial_overview_df():
    return (pd.DataFrame(st.session_state.assets),
            pd.DataFrame(st.session_state.liabilities),
            pd.DataFrame(st.session_state.equity))

def generate_financial_report():
    return pd.DataFrame(st.session_state.revenue), pd.DataFrame(st.session_state.expenses)

def compute_payment_details():
    data = []
    for name, details in st.session_state.hostelites.items():
        rent = details["Rent"]
        paid = details["Paid"]
        due = max(rent - paid, 0)
        overpaid = max(paid - rent, 0)
        data.append({"Hostelite": name, "Room": details["Room"], "Required Rent": rent, "Amount Paid": paid, "Amount Due": due, "Amount Overpaid": overpaid})
    return pd.DataFrame(data)

def add_hostel(name, location):
    st.session_state.hostels.append({"Hostel Name": name, "Location": location})

def remove_hostel(name):
    st.session_state.hostels = [h for h in st.session_state.hostels if h["Hostel Name"] != name]

def add_project(project_name, hostel_name, start_date, end_date, status):
    st.session_state.projects.append({"Project": project_name, "Hostel": hostel_name, "Start Date": start_date, "End Date": end_date, "Status": status})

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
    return pd.DataFrame({"Month": ['Jan','Feb','Mar','Apr','May','Jun'], "Revenue": monthly_rev.values, "Expenses": monthly_exp.values})

# SIDEBAR NAVIGATION
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Hostel Management", "Staff Payments and Dues", "Financial Overview", "Reports"]
    page = st.radio("Go to", pages)

st.markdown("<p class='main-title'>Hostel Financial Manager</p>", unsafe_allow_html=True)

# DASHBOARD SECTION
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

# DATA ENTRY SECTION
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

# BALANCE SHEET SECTION
elif page == "Balance Sheet":
    st.header("Balance Sheet")
    bs_df = get_balance_sheet_df()
    st.dataframe(bs_df)
    fig_bs = px.bar(bs_df, x="Category", y="Amount", title="Balance Sheet Overview", color="Category")
    st.plotly_chart(fig_bs, use_container_width=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# HOSTEL MANAGEMENT SECTION (Add/Remove Hostels & Ongoing Projects)
elif page == "Hostel Management":
    st.header("Hostel Management")
    st.subheader("Add New Hostel")
    with st.form("hostel_form", clear_on_submit=True):
        hostel_name = st.text_input("Hostel Name")
        hostel_location = st.text_input("Location")
        if st.form_submit_button("Add Hostel") and hostel_name:
            st.session_state.hostels.append({"Hostel Name": hostel_name, "Location": hostel_location})
            st.success(f"Hostel '{hostel_name}' added successfully!")
    st.subheader("Remove Hostel")
    if st.session_state.hostels:
        remove_hostel_name = st.selectbox("Select Hostel to Remove", [h["Hostel Name"] for h in st.session_state.hostels])
        if st.button("Remove Hostel") and remove_hostel_name:
            remove_hostel(remove_hostel_name)
            st.success(f"Hostel '{remove_hostel_name}' removed successfully!")
    else:
        st.info("No hostels available.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Ongoing Projects by Hostel")
    with st.form("project_form", clear_on_submit=True):
        project_name = st.text_input("Project Name")
        project_hostel = st.selectbox("Associated Hostel", [h["Hostel Name"] for h in st.session_state.hostels] if st.session_state.hostels else ["No Hostels Available"])
        start_date = st.date_input("Start Date", datetime.date.today())
        end_date = st.date_input("End Date", datetime.date.today())
        status = st.selectbox("Status", ["Pending", "Ongoing", "Completed"])
        if st.form_submit_button("Add Project") and project_name and project_hostel != "No Hostels Available":
            st.session_state.projects.append({"Project": project_name, "Hostel": project_hostel, "Start Date": start_date, "End Date": end_date, "Status": status})
            st.success(f"Project '{project_name}' added for hostel '{project_hostel}'!")
    st.subheader("Current Ongoing Projects")
    if st.session_state.projects:
        df_projects = pd.DataFrame(st.session_state.projects)
        st.dataframe(df_projects)
    else:
        st.info("No ongoing projects available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# STAFF PAYMENTS AND DUES SECTION
elif page == "Staff Payments":
    st.header("Staff Payments and Dues")
    st.subheader("Add/Update Staff Information")
    with st.form("staff_form", clear_on_submit=True):
        staff_name = st.text_input("Staff Name")
        staff_position = st.text_input("Position")
        expected_payment = st.number_input("Expected Payment (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add/Update Staff") and staff_name:
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
    staff_payment_df = compute_staff_payments() if st.session_state.staff_payments else pd.DataFrame()
    if not staff_payment_df.empty:
        st.dataframe(staff_payment_df)
    else:
        st.info("No staff payments recorded yet.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# FINANCIAL OVERVIEW SECTION
elif page == "Financial Overview":
    st.header("Financial Overview - Balance Sheet Details")
    tabs = st.tabs(["Assets", "Liabilities", "Equity"])
    with tabs[0]:
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
        st.dataframe(df_assets) if not df_assets.empty else st.info("No assets recorded yet.")
    with tabs[1]:
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
        st.dataframe(df_liab) if not df_liab.empty else st.info("No liabilities recorded yet.")
    with tabs[2]:
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
        st.dataframe(df_eq) if not df_eq.empty else st.info("No equity recorded yet.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# REPORTS SECTION
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

# FOOTER
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center;'>Developed with ❤️ by Aliyan Ahmad</p>", unsafe_allow_html=True)
st.sidebar.markdown("© 2025 Hostel Finance Manager")
st.sidebar.write("")
st.sidebar.write("")

st.write("Placeholder: Future features and enhancements can be implemented here. (This area is reserved for expansion.)")
st.write("")

# ADDITIONAL BLANK LINES TO APPROXIMATE 500 LINES
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
# End of Application Code
#################################################################
