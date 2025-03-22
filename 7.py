import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state if not already present
if 'hostelites' not in st.session_state:
    st.session_state['hostelites'] = {}
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []
if 'payments' not in st.session_state:
    st.session_state['payments'] = []

# Function to add a hostelite
def add_hostelite(name, room_no, rent):
    st.session_state['hostelites'][name] = {'room_no': room_no, 'rent': rent, 'paid': 0}

# Function to add an expense
def add_expense(category, amount, description, date):
    st.session_state['expenses'].append({'category': category, 'amount': amount, 'description': description, 'date': date})

# Function to record a payment
def add_payment(name, amount, date):
    if name in st.session_state['hostelites']:
        st.session_state['hostelites'][name]['paid'] += amount
        st.session_state['payments'].append({'name': name, 'amount': amount, 'date': date})

# Streamlit UI
st.title("🏠 Hostel Finance & Management System")

# Sidebar navigation
menu = st.sidebar.radio("Navigation", ["Dashboard", "Manage Hostelites", "Track Expenses", "Record Payments"])

if menu == "Dashboard":
    st.header("📊 Financial Overview")
    total_income = sum(h['paid'] for h in st.session_state['hostelites'].values())
    total_expense = sum(e['amount'] for e in st.session_state['expenses'])
    net_balance = total_income - total_expense
    
    st.metric("Total Income", f"Rs. {total_income}")
    st.metric("Total Expenses", f"Rs. {total_expense}")
    st.metric("Net Balance", f"Rs. {net_balance}")
    
    # Expense breakdown chart
    expense_df = pd.DataFrame(st.session_state['expenses'])
    if not expense_df.empty:
        fig, ax = plt.subplots()
        expense_df.groupby("category")["amount"].sum().plot(kind='bar', ax=ax)
        st.pyplot(fig)
    
    # Due payments table
    due_df = pd.DataFrame([{**{'name': k}, **v} for k, v in st.session_state['hostelites'].items()])
    due_df['due'] = due_df['rent'] - due_df['paid']
    st.subheader("📌 Due Payments")
    st.dataframe(due_df[due_df['due'] > 0])

elif menu == "Manage Hostelites":
    st.header("👥 Manage Hostelites")
    with st.form("add_hostelite_form"):
        name = st.text_input("Hostelite Name")
        room_no = st.text_input("Room Number")
        rent = st.number_input("Monthly Rent", min_value=0)
        submitted = st.form_submit_button("Add Hostelite")
        if submitted and name:
            add_hostelite(name, room_no, rent)
            st.success("Hostelite added successfully!")
    
    st.subheader("🏠 Hostelites List")
    st.write(pd.DataFrame(st.session_state['hostelites']).T)

elif menu == "Track Expenses":
    st.header("💰 Track Expenses")
    with st.form("add_expense_form"):
        category = st.selectbox("Expense Category", ["Laundry", "Internet", "Mess", "Maintenance", "Miscellaneous"])
        amount = st.number_input("Amount", min_value=0)
        description = st.text_area("Description")
        date = st.date_input("Date", value=datetime.today())
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            add_expense(category, amount, description, date)
            st.success("Expense recorded successfully!")
    
    st.subheader("📋 Expense Records")
    expense_df = pd.DataFrame(st.session_state['expenses'])
    if not expense_df.empty:
        st.dataframe(expense_df)
    else:
        st.write("No expenses recorded yet.")

elif menu == "Record Payments":
    st.header("💵 Record Payments")
    with st.form("add_payment_form"):
        name = st.selectbox("Select Hostelite", list(st.session_state['hostelites'].keys()))
        amount = st.number_input("Amount", min_value=0)
        date = st.date_input("Date", value=datetime.today())
        submitted = st.form_submit_button("Record Payment")
        if submitted:
            add_payment(name, amount, date)
            st.success("Payment recorded successfully!")
    
    st.subheader("📜 Payment History")
    payment_df = pd.DataFrame(st.session_state['payments'])
    if not payment_df.empty:
        st.dataframe(payment_df)
    else:
        st.write("No payments recorded yet.")
