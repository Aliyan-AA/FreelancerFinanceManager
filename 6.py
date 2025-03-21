import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Hostelite', 'Category', 'Description', 'Amount'])

# App Title
st.title("🏠 Hostel Finance Manager")

# Sidebar for Expense Entry
st.sidebar.header("Add New Expense")

date = st.sidebar.date_input("Date", datetime.today())
hostelite = st.sidebar.text_input("Hostelite Name")
category = st.sidebar.selectbox("Expense Category", ["Hostel Fee", "Laundry", "Internet", "Mess", "Other"])
description = st.sidebar.text_area("Description (Optional)")
amount = st.sidebar.number_input("Amount (PKR)", min_value=0.0, format="%.2f")

if st.sidebar.button("Add Expense"):
    if hostelite and amount > 0:
        new_expense = pd.DataFrame([[date, hostelite, category, description, amount]], 
                                   columns=["Date", "Hostelite", "Category", "Description", "Amount"])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
        st.success(f"Expense added for {hostelite}!")
    else:
        st.error("Please enter valid hostelite name and amount.")

# Display All Expenses
st.subheader("📋 Expense Records")
st.dataframe(st.session_state.expenses)

# Summary Table
st.subheader("💰 Outstanding Balances")
summary = st.session_state.expenses.groupby(["Hostelite"]).sum()["Amount"].reset_index()
st.dataframe(summary)

# Expense Breakdown per Hostelite
st.subheader("📊 Expense Breakdown per Hostelite")
hostelite_selected = st.selectbox("Select Hostelite", st.session_state.expenses["Hostelite"].unique(), index=0)
hostelite_expenses = st.session_state.expenses[st.session_state.expenses["Hostelite"] == hostelite_selected]

total_paid = hostelite_expenses["Amount"].sum()
fig, ax = plt.subplots()
hostelite_expenses.groupby("Category")["Amount"].sum().plot(kind='bar', ax=ax)
ax.set_ylabel("Amount (PKR)")
ax.set_title(f"Expenses Breakdown for {hostelite_selected}")
st.pyplot(fig)

st.write(f"**Total Paid by {hostelite_selected}:** PKR {total_paid:.2f}")
