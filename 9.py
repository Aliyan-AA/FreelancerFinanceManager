import streamlit as st
import pandas as pd
import plotly.express as px

# Set up page configuration
st.set_page_config(page_title="Hostel Finance Manager", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #0051a2;
            text-align: center;
        }
        .sidebar .sidebar-content {
            background-color: #004b8d;
            color: white;
        }
        .metric-box {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #0051a2;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1974/1974895.png", width=150)
    st.subheader("📌 Navigation")
    menu = st.radio("Go to", ["🏠 Dashboard", "💰 Expenses", "🏦 Payments", "📊 Reports"])

# Dashboard Layout
if menu == "🏠 Dashboard":
    st.markdown('<p class="title">🏠 Hostel Finance Dashboard</p>', unsafe_allow_html=True)

    # Financial Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box"><h3>Total Income</h3><h1>PKR 500,000</h1></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><h3>Total Expenses</h3><h1>PKR 320,000</h1></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><h3>Outstanding Dues</h3><h1>PKR 80,000</h1></div>', unsafe_allow_html=True)

    # Charts Section
    st.subheader("📊 Financial Insights")

    # Sample Data for Visualization
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Income": [50000, 60000, 55000, 70000, 65000],
        "Expenses": [30000, 35000, 40000, 42000, 41000],
    })

    # Line Chart
    fig = px.line(df, x="Month", y=["Income", "Expenses"], markers=True, title="Income vs Expenses")
    st.plotly_chart(fig, use_container_width=True)

# Expense Management
elif menu == "💰 Expenses":
    st.markdown('<p class="title">💰 Manage Expenses</p>', unsafe_allow_html=True)
    
    expense_type = st.selectbox("Select Expense Type", ["Laundry", "Internet", "Mess", "Maintenance"])
    amount = st.number_input("Enter Amount (PKR)", min_value=0.0, format="%.2f")
    date = st.date_input("Select Date")
    description = st.text_area("Add Description (Optional)")

    if st.button("Add Expense"):
        st.success(f"{expense_type} expense of PKR {amount} added successfully on {date}.")

# Payment Management
elif menu == "🏦 Payments":
    st.markdown('<p class="title">🏦 Manage Payments</p>', unsafe_allow_html=True)
    
    st.subheader("💳 Record Payment")
    hostelite = st.text_input("Enter Hostelite Name")
    amount_paid = st.number_input("Enter Amount Paid (PKR)", min_value=0.0, format="%.2f")
    payment_date = st.date_input("Payment Date")

    if st.button("Record Payment"):
        st.success(f"Payment of PKR {amount_paid} received from {hostelite} on {payment_date}.")

# Financial Reports
elif menu == "📊 Reports":
    st.markdown('<p class="title">📑 Financial Reports</p>', unsafe_allow_html=True)

    st.subheader("📆 Monthly Report Summary")
    st.write("View a detailed financial breakdown for better planning.")

    # Dummy Data for Report
    report_data = pd.DataFrame({
        "Category": ["Rent", "Utilities", "Maintenance", "Salaries"],
        "Amount (PKR)": [250000, 50000, 30000, 40000]
    })
    
    st.table(report_data)
