#################################################################
# Hostel Financial Management Dashboard with Balance Sheet
# Developed using Streamlit’s Built-in UI Components and Modern CSS
# This application enables hostel owners to analyze and explore
# financial data, view a dynamic balance sheet, and gain valuable
# insights through interactive charts and reports.
#################################################################

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

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
# INITIALIZE SESSION STATE
# ---------------------------------------------------------------
if 'revenue' not in st.session_state:
    st.session_state.revenue = []         # Each revenue entry: Date, Description, Amount
if 'expenses' not in st.session_state:
    st.session_state.expenses = []        # Each expense entry: Date, Category, Description, Amount
if 'balance_sheet' not in st.session_state:
    st.session_state.balance_sheet = {"Assets": 0.0, "Liabilities": 0.0, "Equity": 0.0}
if 'hostel_data' not in st.session_state:
    st.session_state.hostel_data = {}     # Additional hostel-related data if needed

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

def update_balance_sheet():
    total_revenue = sum([entry["Amount"] for entry in st.session_state.revenue])
    total_expenses = sum([entry["Amount"] for entry in st.session_state.expenses])
    # For simplicity, assume Assets = Revenue, Liabilities = Expenses, Equity = Revenue - Expenses
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

def generate_report():
    df_rev = pd.DataFrame(st.session_state.revenue)
    df_exp = pd.DataFrame(st.session_state.expenses)
    return df_rev, df_exp

# ---------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Financial Analysis", "Reports"]
    selection = st.radio("Go to", pages)

# ---------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------
st.markdown("<p class='main-title'>Hostel Financial Manager</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# DASHBOARD SECTION
# ---------------------------------------------------------------
if selection == "Dashboard":
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
# DATA ENTRY SECTION
# ---------------------------------------------------------------
elif selection == "Data Entry":
    st.header("Data Entry")
    tab = st.tabs(["Revenue", "Expense"])
    
    with tab[0]:
        st.subheader("Add Revenue")
        with st.form("revenue_form", clear_on_submit=True):
            rev_date = st.date_input("Date", datetime.date.today())
            rev_desc = st.text_input("Description")
            rev_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Add Revenue"):
                add_revenue(rev_date, rev_desc, rev_amount)
                st.success("Revenue entry added!")
    
    with tab[1]:
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
elif selection == "Balance Sheet":
    st.header("Balance Sheet")
    df_bs = get_balance_sheet_df()
    st.dataframe(df_bs)
    fig_bs = px.bar(df_bs, x="Category", y="Amount", title="Balance Sheet Overview", color="Category")
    st.plotly_chart(fig_bs, use_container_width=True)
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# FINANCIAL ANALYSIS SECTION
# ---------------------------------------------------------------
elif selection == "Financial Analysis":
    st.header("Financial Analysis")
    st.subheader("Interactive Expense Breakdown")
    if st.session_state.expenses:
        df_exp = pd.DataFrame(st.session_state.expenses)
        fig_exp = px.pie(df_exp, values="Amount", names="Category", title="Expense Distribution")
        st.plotly_chart(fig_exp, use_container_width=True)
    else:
        st.info("No expense data to analyze.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Revenue vs Expense Comparison")
    if st.session_state.revenue or st.session_state.expenses:
        rev_total = sum([r["Amount"] for r in st.session_state.revenue])
        exp_total = sum([e["Amount"] for e in st.session_state.expenses])
        comp_df = pd.DataFrame({"Type": ["Revenue", "Expense"], "Amount": [rev_total, exp_total]})
        fig_comp = px.bar(comp_df, x="Type", y="Amount", title="Revenue vs Expense Comparison", color="Type")
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Insufficient data for comparison.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# REPORTS SECTION
# ---------------------------------------------------------------
elif selection == "Reports":
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
    
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.subheader("Combined Financial Report")
    combined_df = pd.concat([df_rev.assign(Type="Revenue"), df_exp.assign(Type="Expense")], ignore_index=True) if not df_rev.empty or not df_exp.empty else pd.DataFrame()
    if not combined_df.empty:
        st.dataframe(combined_df)
        fig_combined = px.histogram(combined_df, x="Type", y="Amount", color="Type", barmode="group", title="Combined Financial Data")
        st.plotly_chart(fig_combined, use_container_width=True)
    else:
        st.info("No combined financial data available.")
    st.markdown("<br>" * 2, unsafe_allow_html=True)

# ---------------------------------------------------------------
# TASK SCHEDULING SECTION
# ---------------------------------------------------------------
elif selection == "Task Scheduling":
    st.header("Task Scheduling & Reminders")
    with st.form("task_form", clear_on_submit=True):
        task_desc = st.text_input("Task Description")
        assigned_to = st.text_input("Assigned To (Staff Name)")
        due_date = st.date_input("Due Date", datetime.date.today())
        task_submit = st.form_submit_button("Schedule Task")
        if task_submit and task_desc:
            st.session_state.tasks.append({"Task": task_desc, "Assigned To": assigned_to, "Due Date": due_date})
            st.success(f"Task scheduled: {task_desc}")
    st.markdown("### Scheduled Tasks")
    if st.session_state.tasks:
        tasks_df = pd.DataFrame(st.session_state.tasks)
        st.dataframe(tasks_df)
    else:
        st.info("No tasks scheduled yet.")

# ---------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center;'>Developed with ❤️ by Aliyan Ahmad</p>", unsafe_allow_html=True)
st.sidebar.markdown("© 2025 Hostel Finance Manager")
for _ in range(10):
    st.write("")
for i in range(50):
    st.write(f"Placeholder line {i+1}: Future features and enhancements can be implemented here.")
st.write("Thank you for using the Hostel Finance Manager!")
#################################################################
# End of Application Code
#################################################################
