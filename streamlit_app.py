import streamlit as st
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

NUM_FUNDS = 200
fund_ids = [f"FUND{str(i).zfill(4)}" for i in range(1, NUM_FUNDS + 1)]
assets = ["Equity", "Bond", "Real Estate", "Private Equity", "Commodities", "Cash", "Crypto"]

def generate_portfolio_data():
    data = []
    for fund_id in fund_ids:
        for _ in range(np.random.randint(5, 20)):
            data.append({
                "fund_id": fund_id,
                "asset_type": random.choice(assets),
                "asset_name": fake.company(),
                "quantity": np.random.randint(100, 10000),
                "price": round(np.random.uniform(10, 500), 2),
                "market_value": lambda q, p: round(q * p, 2),
            })
    df = pd.DataFrame(data)
    df["market_value"] = df.apply(lambda x: round(x["quantity"] * x["price"], 2), axis=1)
    return df

def generate_transaction_data():
    data = []
    for fund_id in fund_ids:
        for _ in range(np.random.randint(10, 50)):
            trade_date = fake.date_between(start_date='-2y', end_date='today')
            data.append({
                "fund_id": fund_id,
                "transaction_id": fake.uuid4(),
                "asset_type": random.choice(assets),
                "trade_date": trade_date,
                "settlement_date": trade_date + timedelta(days=2),
                "action": random.choice(["Buy", "Sell"]),
                "quantity": np.random.randint(10, 500),
                "price": round(np.random.uniform(10, 300), 2),
            })
    df = pd.DataFrame(data)
    df["value"] = df["quantity"] * df["price"]
    return df

def generate_budget_expense_income_data():
    data = []
    for fund_id in fund_ids:
        for year in range(2023, 2026):
            data.append({
                "fund_id": fund_id,
                "year": year,
                "budget": round(np.random.uniform(1e6, 1e8), 2),
                "expenses": round(np.random.uniform(5e5, 9e7), 2),
                "income": round(np.random.uniform(5e5, 1e7), 2),
            })
    return pd.DataFrame(data)

def generate_corporate_actions_data():
    actions = ["Dividend", "Split", "Merger", "Spin-off", "Bonus Issue"]
    data = []
    for _ in range(1000):
        data.append({
            "fund_id": random.choice(fund_ids),
            "action_id": fake.uuid4(),
            "action_type": random.choice(actions),
            "action_date": fake.date_between(start_date='-1y', end_date='today'),
            "description": fake.text(max_nb_chars=50)
        })
    return pd.DataFrame(data)

def generate_investor_flows():
    data = []
    for fund_id in fund_ids:
        for _ in range(np.random.randint(10, 50)):
            data.append({
                "fund_id": fund_id,
                "investor_id": fake.uuid4(),
                "flow_type": random.choice(["Subscription", "Redemption"]),
                "flow_date": fake.date_between(start_date='-2y', end_date='today'),
                "amount": round(np.random.uniform(1e4, 1e6), 2),
            })
    return pd.DataFrame(data)

def generate_aml_data():
    data = []
    for _ in range(1000):
        data.append({
            "investor_id": fake.uuid4(),
            "name": fake.name(),
            "country": fake.country(),
            "transaction_amount": round(np.random.uniform(1e3, 1e6), 2),
            "flagged": random.choices(["Yes", "No"], weights=[0.05, 0.95])[0],
            "flag_reason": random.choice(["None", "High-risk country", "Large transaction", "PEP"]) if random.random() < 0.05 else "None"
        })
    return pd.DataFrame(data)

def generate_investor_register():
    data = []
    for _ in range(1500):
        data.append({
            "investor_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "address": fake.address(),
            "country": fake.country(),
            "registered_date": fake.date_between(start_date='-3y', end_date='today'),
        })
    return pd.DataFrame(data)

# Streamlit UI
st.set_page_config(layout="wide", page_title="Synthetic Fund Accounting Data")

st.title("🧪 Synthetic Fund Accounting Data Generator")

tabs = st.tabs([
    "Portfolio", "Transactions", "Budget & Financials",
    "Corporate Actions", "Investor Flows", "AML Data", "Investor Register"
])

with tabs[0]:
    st.subheader("📊 Portfolio Data")
    df_portfolio = generate_portfolio_data()
    st.dataframe(df_portfolio)

with tabs[1]:
    st.subheader("🔁 Transactions")
    df_transactions = generate_transaction_data()
    st.dataframe(df_transactions)

with tabs[2]:
    st.subheader("💰 Budgets, Expenses, Income")
    df_budget = generate_budget_expense_income_data()
    st.dataframe(df_budget)

with tabs[3]:
    st.subheader("🏢 Corporate Actions")
    df_actions = generate_corporate_actions_data()
    st.dataframe(df_actions)

with tabs[4]:
    st.subheader("📥 Investor Flows")
    df_flows = generate_investor_flows()
    st.dataframe(df_flows)

with tabs[5]:
    st.subheader("🚨 AML Data")
    df_aml = generate_aml_data()
    st.dataframe(df_aml)

with tabs[6]:
    st.subheader("🧾 Investor Register")
    df_register = generate_investor_register()
    st.dataframe(df_register)
