import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state for hostel data
if 'hostel_data' not in st.session_state:
    st.session_state.hostel_data = pd.DataFrame(columns=["Date", "Name", "Laundry", "Internet", "Mess", "Other Expenses", "Expense Description", "Total Due", "Paid", "Balance"])

st.title("🏠 Hostel Finance Manager")
st.write("Manage hostel expenses and track payments effectively.")

# Input for adding a hostelite
st.subheader("➕ Add a Hostelite")
name = st.text_input("Enter hostelite's name:")
date = st.date_input("Select Date:", datetime.today())
laundry = st.number_input("Laundry Fee (Rs.)", min_value=0, value=500, step=50)
internet = st.number_input("Internet Fee (Rs.)", min_value=0, value=300, step=50)
mess = st.number_input("Mess Fee (Rs.)", min_value=0, value=5000, step=500)
other = st.number_input("Other Expenses (Rs.)", min_value=0, value=0, step=100)
description = st.text_area("Expense Description (optional)")
paid = st.number_input("Amount Paid (Rs.)", min_value=0, value=0, step=100)

if st.button("Add Hostelite"):
    total_due = laundry + internet + mess + other
    balance = paid - total_due
    new_entry = pd.DataFrame([[date, name, laundry, internet, mess, other, description, total_due, paid, balance]],
                             columns=st.session_state.hostel_data.columns)
    st.session_state.hostel_data = pd.concat([st.session_state.hostel_data, new_entry], ignore_index=True)
    st.success(f"Added {name} to the hostel records on {date}.")

# Display Hostel Data
st.subheader("📜 Hostel Payment Records")
st.dataframe(st.session_state.hostel_data)

# Filters for hostelites who owe money or have overpaid
st.subheader("🔍 Payment Status")

def filter_hostelites(status):
    if status == "Owe Money":
        return st.session_state.hostel_data[st.session_state.hostel_data["Balance"] < 0]
    elif status == "Overpaid":
        return st.session_state.hostel_data[st.session_state.hostel_data["Balance"] > 0]
    else:
        return st.session_state.hostel_data[st.session_state.hostel_data["Balance"] == 0]

status_filter = st.selectbox("Select payment status:", ["All", "Owe Money", "Paid in Full", "Overpaid"])
filtered_data = filter_hostelites(status_filter) if status_filter != "All" else st.session_state.hostel_data
st.dataframe(filtered_data)

# Allowing updates
st.subheader("✏️ Update Payments")
selected_name = st.selectbox("Select hostelite to update:", st.session_state.hostel_data["Name"].unique() if not st.session_state.hostel_data.empty else [])
new_payment = st.number_input("Enter additional payment (Rs.):", min_value=0, value=0, step=100)

if st.button("Update Payment"):
    index = st.session_state.hostel_data[st.session_state.hostel_data["Name"] == selected_name].index[0]
    st.session_state.hostel_data.at[index, "Paid"] += new_payment
    st.session_state.hostel_data.at[index, "Balance"] = st.session_state.hostel_data.at[index, "Paid"] - st.session_state.hostel_data.at[index, "Total Due"]
    st.success(f"Updated payment for {selected_name}.")

# Summary Statistics
st.subheader("📊 Summary Statistics")
total_due = st.session_state.hostel_data["Total Due"].sum()
total_paid = st.session_state.hostel_data["Paid"].sum()
total_balance = st.session_state.hostel_data["Balance"].sum()
st.write(f"**Total Due:** Rs. {total_due}")
st.write(f"**Total Paid:** Rs. {total_paid}")
st.write(f"**Net Balance:** Rs. {total_balance}")

# Graphs for each hostelite
st.subheader("📈 Individual Expense Breakdown")
hostelite_names = st.session_state.hostel_data["Name"].unique()
selected_graph_name = st.selectbox("Select hostelite for graph:", hostelite_names if len(hostelite_names) > 0 else ["None"])

if selected_graph_name != "None":
    selected_data = st.session_state.hostel_data[st.session_state.hostel_data["Name"] == selected_graph_name]
    if not selected_data.empty:
        expense_labels = ["Laundry", "Internet", "Mess", "Other Expenses"]
        expense_values = [selected_data.iloc[0]["Laundry"], selected_data.iloc[0]["Internet"], selected_data.iloc[0]["Mess"], selected_data.iloc[0]["Other Expenses"]]
        
        fig, ax = plt.subplots()
        ax.pie(expense_values, labels=expense_labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

st.write("📌 Now you can track expenses with detailed breakdowns, dates, and graphs for better insights!")
