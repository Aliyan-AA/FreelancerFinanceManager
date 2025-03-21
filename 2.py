import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import pdfkit
from io import BytesIO

# Initialize session state if not already done
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'clients' not in st.session_state:
    st.session_state.clients = []
if 'goals' not in st.session_state:
    st.session_state.goals = []
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = []
if 'expense_categories' not in st.session_state:
    st.session_state.expense_categories = {"Project": 0, "Marketing": 0, "Tools": 0, "Other": 0}

# Function to add a transaction
def add_transaction(type, amount, description, date, category, client):
    st.session_state.transactions.append({
        'Type': type,
        'Amount': amount,
        'Description': description,
        'Date': date,
        'Category': category,
        'Client': client
    })
    if type == "Expense":
        st.session_state.expense_categories[category] += amount

# Function to add a client
def add_client(name, contact):
    st.session_state.clients.append({
        'Name': name,
        'Contact': contact
    })

# Function to calculate tax estimation
def calculate_tax(income):
    tax_rate = 0.15  # Assuming a 15% tax rate
    return income * tax_rate

# Function to generate an invoice
def generate_invoice(client, amount, description, date):
    invoice_html = f"""
    <html>
    <body>
        <h2>Invoice</h2>
        <p><strong>Client:</strong> {client}</p>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Amount:</strong> ${amount:.2f}</p>
        <p><strong>Date:</strong> {date}</p>
    </body>
    </html>
    """
    pdf = pdfkit.from_string(invoice_html, False)
    return pdf

# Function to set reminders
def add_reminder(reminder_text, due_date):
    st.session_state.reminders.append({
        "Reminder": reminder_text,
        "Due Date": due_date
    })

# Function to add subscriptions
def add_subscription(name, cost, renewal_date):
    st.session_state.subscriptions.append({
        "Name": name,
        "Cost": cost,
        "Renewal Date": renewal_date
    })

# Streamlit UI
st.set_page_config(page_title="Freelancer Finance Manager", layout="wide")
st.title("💼 Freelancer Finance Manager")

# Sidebar for quick navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Transactions", "Clients", "Financial Summary", "Goals", "Invoices", "Reminders", "Subscriptions", "Expense Analysis"])

if page == "Transactions":
    st.header("💰 Add a New Transaction")
    type = st.selectbox("Transaction Type", ["Income", "Expense"])
    amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
    description = st.text_input("Description")
    date = st.date_input("Date", datetime.date.today())
    category = st.selectbox("Category", ["Project", "Marketing", "Tools", "Other"])
    client = st.selectbox("Client", [c['Name'] for c in st.session_state.clients] + ["None"])
    if st.button("Add Transaction"):
        add_transaction(type, amount, description, date, category, client)
        st.success("Transaction added successfully!")
    
    transactions_df = pd.DataFrame(st.session_state.transactions)
    if not transactions_df.empty:
        st.subheader("📜 Transaction History")
        st.dataframe(transactions_df)

if page == "Expense Analysis":
    st.header("📊 Expense Analysis")
    categories = list(st.session_state.expense_categories.keys())
    values = list(st.session_state.expense_categories.values())
    if sum(values) > 0:
        fig, ax = plt.subplots()
        ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
    else:
        st.info("No expenses recorded yet.")

if page == "Subscriptions":
    st.header("🔔 Manage Subscriptions")
    sub_name = st.text_input("Subscription Name")
    sub_cost = st.number_input("Cost ($)", min_value=0.0, format="%.2f")
    sub_date = st.date_input("Renewal Date")
    if st.button("Add Subscription"):
        add_subscription(sub_name, sub_cost, sub_date)
        st.success("Subscription added successfully!")
    
    subs_df = pd.DataFrame(st.session_state.subscriptions)
    if not subs_df.empty:
        st.subheader("📌 Your Subscriptions")
        st.dataframe(subs_df)

if page == "Financial Summary":
    transactions_df = pd.DataFrame(st.session_state.transactions)
    if not transactions_df.empty:
        total_income = transactions_df[transactions_df['Type'] == 'Income']['Amount'].sum()
        total_expense = transactions_df[transactions_df['Type'] == 'Expense']['Amount'].sum()
        balance = total_income - total_expense
        estimated_tax = calculate_tax(total_income)
        
        st.subheader("📊 Financial Summary")
        st.write(f"**Total Income:** ${total_income:.2f}")
        st.write(f"**Total Expenses:** ${total_expense:.2f}")
        st.write(f"**Balance:** ${balance:.2f}")
        st.write(f"**Estimated Tax (15%):** ${estimated_tax:.2f}")
        
        st.subheader("📉 Income vs Expenses")
        st.bar_chart(transactions_df.groupby("Type")["Amount"].sum())
    else:
        st.info("No transactions recorded yet.")
