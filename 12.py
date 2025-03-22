import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Title of the application
st.title("Hostel Financial Management System")

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select a page:", ["Dashboard", "Hostel Management", "Financial Management", "Future Enhancements"])

# Function to simulate financial data
def generate_financial_data():
    data = {
        "Month": pd.date_range(start="2023-01-01", periods=12, freq='M'),
        "Income": np.random.randint(8000, 12000, size=12),
        "Expenses": np.random.randint(5000, 9000, size=12),
    }
    df = pd.DataFrame(data)
    df['Net Income'] = df['Income'] - df['Expenses']
    return df

# Dashboard Page
if page == "Dashboard":
    st.header("Financial Dashboard")
    
    financial_data = generate_financial_data()
    
    # Display financial data
    st.subheader("Monthly Financial Overview")
    st.write(financial_data)

    # Plotting Income and Expenses
    plt.figure(figsize=(10, 5))
    plt.plot(financial_data['Month'], financial_data['Income'], label='Income', marker='o')
    plt.plot(financial_data['Month'], financial_data['Expenses'], label='Expenses', marker='o')
    plt.fill_between(financial_data['Month'], financial_data['Income'], financial_data['Expenses'], 
                     where=(financial_data['Income'] > financial_data['Expenses']), 
                     color='green', alpha=0.3, label='Net Positive')
    plt.fill_between(financial_data['Month'], financial_data['Income'], financial_data['Expenses'], 
                     where=(financial_data['Income'] <= financial_data['Expenses']), 
                     color='red', alpha=0.3, label='Net Negative')
    plt.title("Monthly Income and Expenses")
    plt.xlabel("Month")
    plt.ylabel("Amount ($)")
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)

    # Cost Reduction Suggestions
    st.subheader("Cost Reduction Suggestions")
    st.write("1. Implement energy-saving initiatives.")
    st.write("2. Negotiate better rates with suppliers.")
    st.write("3. Regularly review service contracts.")

# Hostel Management Page
elif page == "Hostel Management":
    st.header("Hostel Management")
    
    # Add hostel buildings
    st.subheader("Add Hostel Building")
    building_name = st.text_input("Building Name")
    num_rooms = st.number_input("Number of Rooms", min_value=1)
    
    if st.button("Add Building"):
        st.success(f"Building '{building_name}' with {num_rooms} rooms added.")

    # Room Availability
    st.subheader("Room Availability")
    st.write("Total Rooms: ", num_rooms)

# Financial Management Page
elif page == "Financial Management":
    st.header("Financial Management")
    
    # Add monthly expenses
    st.subheader("Add Monthly Expenses")
    expense_category = st.selectbox("Select Expense Category", ["Electricity", "Water", "WiFi", "Maintenance", "Salaries"])
    expense_amount = st.number_input("Expense Amount", min_value=0.0)

    if st.button("Add Expense"):
        st.success(f"Added {expense_amount} for {expense_category}.")

    # Income tracking
    st.subheader("Track Income from Hostelites")
    income_amount = st.number_input("Income Amount", min_value=0.0)

    if st.button("Add Income"):
        st.success(f"Added {income_amount} income.")

# Future Enhancements Page
elif page == "Future Enhancements":
    st.header("Future Features and Enhancements")
    st.write("1. Integration with accounting software (QuickBooks, etc.).")
    st.write("2. Automated reporting and alerts for financial metrics.")
    st.write("3. Mobile app for easier access and management.")
    st.write("4. Advanced analytics for forecasting and budgeting.")
    st.write("5. User feedback section to understand needs better.")

# Footer
st.sidebar.write("Developed by [Your Name]")
st.sidebar.write("Version 1.0")

# Fix for future features section printing repeatedly
if 'future_features_displayed' not in st.session_state:
    st.session_state.future_features_displayed = True
