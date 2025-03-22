import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Hostelite"])

if 'payments' not in st.session_state:
    st.session_state.payments = pd.DataFrame(columns=["Date", "Hostelite", "Amount Paid"])

if 'hostelites' not in st.session_state:
    st.session_state.hostelites = []

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Function to add an expense
def add_expense():
    st.subheader("Add Expense")
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Rent", "Laundry", "Internet", "Mess", "Maintenance", "Other"])
    description = st.text_area("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    hostelite = st.selectbox("Hostelite", st.session_state.hostelites)
    
    if st.button("Add Expense"):
        new_expense = pd.DataFrame([[date, category, description, amount, hostelite]], columns=["Date", "Category", "Description", "Amount", "Hostelite"])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
        st.success("Expense Added Successfully!")

# Function to add payment
def add_payment():
    st.subheader("Add Payment")
    date = st.date_input("Date", datetime.today())
    hostelite = st.selectbox("Hostelite", st.session_state.hostelites)
    amount_paid = st.number_input("Amount Paid", min_value=0.0, format="%.2f")
    
    if st.button("Add Payment"):
        new_payment = pd.DataFrame([[date, hostelite, amount_paid]], columns=["Date", "Hostelite", "Amount Paid"])
        st.session_state.payments = pd.concat([st.session_state.payments, new_payment], ignore_index=True)
        st.success("Payment Added Successfully!")

# Function to manage hostelites
def manage_hostelites():
    st.subheader("Manage Hostelites")
    name = st.text_input("Hostelite Name")
    
    if st.button("Add Hostelite"):
        if name not in st.session_state.hostelites:
            st.session_state.hostelites.append(name)
            st.success("Hostelite Added Successfully!")
        else:
            st.warning("Hostelite Already Exists!")

# Function to view reports
def view_reports():
    st.subheader("Financial Reports")
    
    if not st.session_state.expenses.empty:
        st.write("### Expenses Overview")
        st.dataframe(st.session_state.expenses)
        
        fig, ax = plt.subplots()
        st.session_state.expenses.groupby("Category")["Amount"].sum().plot(kind="bar", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No expenses recorded yet.")
    
    if not st.session_state.payments.empty:
        st.write("### Payments Overview")
        st.dataframe(st.session_state.payments)
    else:
        st.warning("No payments recorded yet.")
    
# Function to schedule maintenance
def schedule_maintenance():
    st.subheader("Schedule Maintenance & Tasks")
    task = st.text_input("Task Description")
    date = st.date_input("Schedule Date", datetime.today())
    
    if st.button("Add Task"):
        st.session_state.tasks.append({"Task": task, "Date": date})
        st.success("Task Scheduled Successfully!")
    
    if st.session_state.tasks:
        st.write("### Scheduled Tasks")
        task_df = pd.DataFrame(st.session_state.tasks)
        st.dataframe(task_df)
    else:
        st.warning("No tasks scheduled yet.")

# Streamlit Navigation
st.title("🏠 Hostel Finance & Management System")
menu = st.sidebar.radio("Navigation", ["Add Expense", "Add Payment", "Manage Hostelites", "Financial Reports", "Schedule Maintenance"])

if menu == "Add Expense":
    add_expense()
elif menu == "Add Payment":
    add_payment()
elif menu == "Manage Hostelites":
    manage_hostelites()
elif menu == "Financial Reports":
    view_reports()
elif menu == "Schedule Maintenance":
    schedule_maintenance()
