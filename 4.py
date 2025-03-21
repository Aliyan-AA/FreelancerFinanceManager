import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Initialize session state for jars
if 'jars' not in st.session_state:
    st.session_state.jars = {
        "Essentials": 50,
        "Savings": 20,
        "Investments": 15,
        "Entertainment": 10,
        "Charity": 5
    }

st.title("🏦 Virtual Finance Jar System")
st.write("Gamified Envelope Budgeting to manage your money wisely!")

# Input for Monthly Income
income = st.number_input("Enter your monthly income:", min_value=0, value=50000, step=1000)

def update_budget(jar, amount):
    if jar in st.session_state.jars and 0 <= amount <= 100:
        st.session_state.jars[jar] = amount

def display_jars():
    """Display finance jars as a pie chart."""
    labels = list(st.session_state.jars.keys())
    sizes = list(st.session_state.jars.values())
    colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFD700", "#FF66B2"]
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

# Editable Allocation
st.subheader("💡 Customize Your Budget Jars")
for jar in st.session_state.jars:
    new_value = st.slider(f"{jar} (%)", 0, 100, st.session_state.jars[jar])
    update_budget(jar, new_value)

display_jars()

# Calculating actual allocations
st.subheader("📊 Your Monthly Budget Allocation")
allocation_data = {jar: (income * (percent / 100)) for jar, percent in st.session_state.jars.items()}
budget_df = pd.DataFrame(list(allocation_data.items()), columns=["Jar", "Amount (Rs.)"])
st.dataframe(budget_df)

# Gamification
st.subheader("🎯 Financial Challenge of the Month")
st.write("Save 10% more in your Savings jar this month to unlock a surprise reward!")

if st.button("Claim Reward 🎁"):
    if st.session_state.jars["Savings"] >= 30:
        st.success("🎉 Congratulations! You've unlocked a 1-month premium subscription to a financial newsletter!")
    else:
        st.warning("💡 Try increasing your savings jar to claim the reward!")
