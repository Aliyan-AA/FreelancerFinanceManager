import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Financial Personality Types
def get_financial_personality(score):
    if score <= 10:
        return "The Spender", "You love to spend, but savings take a backseat! Try to allocate some income towards investments."
    elif 11 <= score <= 20:
        return "The Minimalist", "You spend wisely and prioritize needs over wants. Consider strategic investments for future growth."
    elif 21 <= score <= 30:
        return "The Saver", "You have excellent saving habits. Ensure you also invest to grow wealth over time."
    elif 31 <= score <= 40:
        return "The Investor", "You focus on wealth creation. Diversify your investments to minimize risks."
    else:
        return "The Balanced Individual", "You maintain a good balance between spending, saving, and investing. Keep it up!"

# Questions for Quiz
questions = [
    ("How often do you impulse buy?", ["Always", "Often", "Sometimes", "Rarely", "Never"], [1, 2, 3, 4, 5]),
    ("What percentage of your income do you save?", ["0-10%", "11-20%", "21-30%", "31-40%", "More than 40%"], [1, 2, 3, 4, 5]),
    ("Do you track your expenses?", ["Never", "Rarely", "Sometimes", "Often", "Always"], [1, 2, 3, 4, 5]),
    ("How comfortable are you with investing?", ["Not at all", "A little", "Somewhat", "Very", "Extremely"], [1, 2, 3, 4, 5]),
    ("Do you plan your purchases ahead?", ["Never", "Rarely", "Sometimes", "Often", "Always"], [1, 2, 3, 4, 5])
]

# Streamlit UI
st.title("💰 Financial Karma: Your Money Personality Tracker")
st.write("Answer a few questions to discover your financial personality!")

total_score = 0
for q, options, scores in questions:
    choice = st.radio(q, options)
    total_score += scores[options.index(choice)]

if st.button("Get My Financial Personality"):
    personality, advice = get_financial_personality(total_score)
    st.subheader(f"🧠 You are: {personality}")
    st.write(f"📌 {advice}")

    # Spending Habit Visualization
    st.subheader("📊 Your Financial Behavior")
    categories = ["Spending", "Saving", "Investing"]
    values = [total_score * 2, 50 - total_score, total_score - 10]
    values = [max(v, 0) for v in values]  # Ensure no negative values
    
    fig, ax = plt.subplots()
    ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=140, colors=['red', 'green', 'blue'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    st.pyplot(fig)

    st.write("🎯 Try setting a financial goal to improve your habits!")