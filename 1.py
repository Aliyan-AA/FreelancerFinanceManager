import streamlit as st
import pandas as pd
import datetime

# Initialize session state if not already done
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Function to add a transaction
def add_transaction(type, amount, description, date):
    st.session_state.transactions.append({
        'Type': type,
        'Amount': amount,
        'Description': description,
        'Date': date
    })

# Function to calculate tax estimation
def calculate_tax(income):
    tax_rate = 0.15  # Assuming a 15% tax rate
    return income * tax_rate

# Streamlit UI
st.title("Freelancer Finance Manager")

# Section: Add Transaction
st.header("Add a New Transaction")
type = st.selectbox("Transaction Type", ["Income", "Expense"])
amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
description = st.text_input("Description")
date = st.date_input("Date", datetime.date.today())
if st.button("Add Transaction"):
    add_transaction(type, amount, description, date)
    st.success("Transaction added successfully!")

# Convert transactions to DataFrame
transactions_df = pd.DataFrame(st.session_state.transactions)

# Section: Display Transactions
if not transactions_df.empty:
    st.header("Transaction History")
    st.dataframe(transactions_df)
    
    # Calculate Summary
    total_income = transactions_df[transactions_df['Type'] == 'Income']['Amount'].sum()
    total_expense = transactions_df[transactions_df['Type'] == 'Expense']['Amount'].sum()
    balance = total_income - total_expense
    estimated_tax = calculate_tax(total_income)
    
    # Display Summary
    st.subheader("Financial Summary")
    st.write(f"**Total Income:** ${total_income:.2f}")
    st.write(f"**Total Expenses:** ${total_expense:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")
    st.write(f"**Estimated Tax (15%):** ${estimated_tax:.2f}")
    
    # Visualization
    st.subheader("Income vs Expenses")
    st.bar_chart(transactions_df.groupby("Type")["Amount"].sum())
else:
    st.info("No transactions recorded yet.")
