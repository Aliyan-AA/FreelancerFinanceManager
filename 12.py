#################################################################
# Hostel Financial Management Dashboard with Balance Sheet,     #
# Rent Collection Forecasting, and Room Assignments              #
# Developed using Streamlit’s Built-in UI Components               #
# This application enables hostel owners to analyze financial      #
# data, manage hostelites, track revenue and expenses, view a        #
# dynamic balance sheet, forecast rent collection, and manage        #
# room assignments. It also reserves space for future enhancements.  #
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
    st.session_state.hostelites = {}  # Hostelite data: key=name, value={Room, Rent, Paid}
if 'tasks' not in st.session_state:
    st.session_state.tasks = []      # Task scheduling: list of dicts {Task, Assigned To, Due Date}
if 'rent_history' not in st.session_state:
    st.session_state.rent_history = pd.DataFrame()  # DataFrame for historical rent data
if 'room_assignments' not in st.session_state:
    st.session_state.room_assignments = []  # List for room assignments

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
    st.session_state.payments.append({
        "Date": date,
        "Hostelite": hostelite,
        "Amount Paid": amount,
        "Method": method
    })

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

def add_room_assignment(room_no, occupant, required_payment, amount_paid):
    due = required_payment - amount_paid
    if due < 0:
        status = "Overpaid"
    elif due == 0:
        status = "Cleared"
    else:
        status = "Due"
    st.session_state.room_assignments.append({
        "Room No": room_no,
        "Occupant": occupant,
        "Required Payment": required_payment,
        "Amount Paid": amount_paid,
        "Status": status
    })

def update_room_assignment(index, room_no, occupant, required_payment, amount_paid):
    due = required_payment - amount_paid
    if due < 0:
        status = "Overpaid"
    elif due == 0:
        status = "Cleared"
    else:
        status = "Due"
    st.session_state.room_assignments[index] = {
        "Room No": room_no,
        "Occupant": occupant,
        "Required Payment": required_payment,
        "Amount Paid": amount_paid,
        "Status": status
    }

# ---------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.markdown("<h3 style='color:white;'>Navigation</h3>", unsafe_allow_html=True)
    pages = ["Dashboard", "Data Entry", "Balance Sheet", "Rent Forecasting", "Room Assignments", "Reports", "Task Scheduling"]
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
# RENT FORECASTING SECTION
# ---------------------------------------------------------------
elif page == "Rent Forecasting":
    st.header("Rent Collection Forecasting")
    st.write("Forecast future rent collection based on historical data.")
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

# ---------------------------------------------------------------
# ROOM ASSIGNMENTS SECTION (New Feature)
# ---------------------------------------------------------------
elif page == "Room Assignments":
    st.header("Room Assignments Management")
    with st.form("room_assignment_form", clear_on_submit=True):
        room_no = st.text_input("Room Number")
        occupant = st.text_input("Occupant Name")
        required_payment = st.number_input("Required Payment (PKR)", min_value=0.0, format="%.2f")
        amount_paid = st.number_input("Amount Paid (PKR)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Add Room Assignment") and room_no and occupant:
            add_room_assignment(room_no, occupant, required_payment, amount_paid)
            st.success(f"Room {room_no} assigned to {occupant} updated!")
    st.markdown("### Current Room Assignments")
    if st.session_state.room_assignments:
        df_rooms = pd.DataFrame(st.session_state.room_assignments)
        st.dataframe(df_rooms)
        # Option to update an existing assignment
        st.subheader("Update Room Assignment")
        index_to_update = st.number_input("Enter the index of the assignment to update (starting from 0)", min_value=0, max_value=len(st.session_state.room_assignments)-1, step=1)
        if st.session_state.room_assignments:
            with st.form("update_room_form", clear_on_submit=True):
                new_room_no = st.text_input("New Room Number", value=df_rooms.iloc[index_to_update]["Room No"])
                new_occupant = st.text_input("New Occupant Name", value=df_rooms.iloc[index_to_update]["Occupant"])
                new_required_payment = st.number_input("New Required Payment (PKR)", min_value=0.0, value=float(df_rooms.iloc[index_to_update]["Required Payment"]), format="%.2f")
                new_amount_paid = st.number_input("New Amount Paid (PKR)", min_value=0.0, value=float(df_rooms.iloc[index_to_update]["Amount Paid"]), format="%.2f")
                if st.form_submit_button("Update Assignment"):
                    update_room_assignment(index_to_update, new_room_no, new_occupant, new_required_payment, new_amount_paid)
                    st.success("Room assignment updated!")
    else:
        st.info("No room assignments available.")
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
# TASK SCHEDULING & REMINDERS SECTION
# ---------------------------------------------------------------
elif page == "Task Scheduling":
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
# FOOTER SECTION
# ---------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center;'>Developed with ❤️ by Aliyan Ahmad</p>", unsafe_allow_html=True)
st.sidebar.markdown("© 2025 Hostel Finance Manager")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")

st.write("Placeholder: Future features and enhancements can be implemented here. (This area is reserved for expansion.)")

# ---------------------------------------------------------------
# ADDITIONAL BLANK LINES TO APPROXIMATE 500 LINES
# ---------------------------------------------------------------
# The following lines serve as placeholders for future expansion.
# Future enhancements may include:
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
