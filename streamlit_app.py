import streamlit as st
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import duckdb
import plotly.express as px
from io import BytesIO

fake = Faker()

# Sidebar controls
st.set_page_config(layout="wide", page_title="Synthetic Fund Accounting Data")

# --- Authentication ---
USER_CREDENTIALS = {"admin": "pass123", "analyst": "fund2025"}
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("🔐 Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state['authenticated'] = True
            st.success("Logged in!")
        else:
            st.error("Invalid credentials")
    st.stop()

st.title("🧪 Synthetic Fund Accounting Data Generator")

# Asset types
default_assets = ["Equity", "Bond", "Real Estate", "Private Equity", "Commodities", "Cash", "Crypto"]
assets = st.sidebar.multiselect("Select Asset Types", default_assets, default=default_assets)
num_funds = st.sidebar.slider("Number of Funds", 10, 500, 200, step=10)
num_assets = st.sidebar.slider("Avg. Assets per Fund", 5, 30, 10)

accounting_rate = st.sidebar.number_input("Accounting Rate (bps)", min_value=0.0, value=1.0)
custody_rate = st.sidebar.number_input("Custody Rate (bps)", min_value=0.0, value=0.5)
ta_rate = st.sidebar.number_input("TA Rate (bps)", min_value=0.0, value=0.3)

if 'regen' not in st.session_state:
    st.session_state['regen'] = True

if st.sidebar.button("🔄 Regenerate Data"):
    st.session_state['regen'] = True

fund_ids = [f"FUND{str(i).zfill(4)}" for i in range(1, num_funds + 1)]

# --- Data Generators ---
def generate_portfolio_data():
    data = []
    for fund_id in fund_ids:
        for _ in range(random.randint(num_assets//2, num_assets*2)):
            asset_type = random.choice(assets)
            quantity = np.random.randint(100, 10000)
            price = round(np.random.uniform(10, 500), 2)
            data.append({
                "fund_id": fund_id,
                "asset_type": asset_type,
                "asset_name": fake.company(),
                "quantity": quantity,
                "price": price,
                "market_value": round(quantity * price, 2),
                "country_of_risk": fake.country(),
                "currency": random.choice(["USD", "EUR", "GBP", "JPY"]),
                "issuer_rating": random.choice(["AAA", "AA", "A", "BBB", "BB", "NR"])
            })
    return pd.DataFrame(data)

def generate_transaction_data():
    data = []
    for fund_id in fund_ids:
        for _ in range(random.randint(10, 30)):
            date = fake.date_between('-2y', 'today')
            quantity = np.random.randint(10, 1000)
            price = round(np.random.uniform(5, 300), 2)
            data.append({
                "fund_id": fund_id,
                "transaction_id": fake.uuid4(),
                "asset_type": random.choice(assets),
                "trade_date": date,
                "settlement_date": date + timedelta(days=2),
                "action": random.choice(["Buy", "Sell"]),
                "quantity": quantity,
                "price": price,
                "value": quantity * price
            })
    return pd.DataFrame(data)

def generate_budget_data():
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

def generate_corporate_actions():
    actions = ["Dividend", "Split", "Merger", "Spin-off"]
    data = []
    for _ in range(500):
        data.append({
            "fund_id": random.choice(fund_ids),
            "action_id": fake.uuid4(),
            "action_type": random.choice(actions),
            "action_date": fake.date_between('-1y', 'today'),
            "description": fake.sentence()
        })
    return pd.DataFrame(data)

def generate_investor_flows():
    data = []
    for fund_id in fund_ids:
        for _ in range(random.randint(5, 15)):
            data.append({
                "fund_id": fund_id,
                "investor_id": fake.uuid4(),
                "flow_type": random.choice(["Subscription", "Redemption"]),
                "flow_date": fake.date_between('-2y', 'today'),
                "amount": round(np.random.uniform(1e4, 1e6), 2)
            })
    return pd.DataFrame(data)

def generate_aml_data():
    data = []
    for _ in range(1000):
        flagged = random.choices(["Yes", "No"], weights=[0.05, 0.95])[0]
        data.append({
            "investor_id": fake.uuid4(),
            "name": fake.name(),
            "country": fake.country(),
            "transaction_amount": round(np.random.uniform(1e3, 1e6), 2),
            "flagged": flagged,
            "flag_reason": random.choice(["High-risk country", "Large transaction", "PEP", "None"]) if flagged == "Yes" else "None"
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
            "registered_date": fake.date_between('-3y', 'today')
        })
    return pd.DataFrame(data)

def calculate_servicing_cost(df):
    rates = {"Equity": 0.0005, "Bond": 0.0004, "Real Estate": 0.001, "Private Equity": 0.0015,
             "Commodities": 0.0008, "Cash": 0.0002, "Crypto": 0.001}
    mix = df.groupby(["fund_id", "asset_type"])["market_value"].sum().reset_index()
    mix["service_cost"] = mix.apply(lambda x: x.market_value * rates.get(x.asset_type, 0), axis=1)
    return mix.groupby("fund_id")["service_cost"].sum().reset_index(name="servicing_cost")

def calculate_admin_costs(df):
    mv = df.groupby("fund_id")["market_value"].sum().reset_index()
    mv["accounting"] = mv["market_value"] * accounting_rate / 10000
    mv["custody"] = mv["market_value"] * custody_rate / 10000
    mv["ta"] = mv["market_value"] * ta_rate / 10000
    mv["total_admin_cost"] = mv[["accounting", "custody", "ta"]].sum(axis=1)
    return mv

def send_to_motherduck(df_dict):
    con = duckdb.connect("md:your_project/your_db")  # Replace with your actual MotherDuck project/db
    for name, df in df_dict.items():
        con.execute(f"DROP TABLE IF EXISTS {name}")
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM df")
    st.success("✅ Data uploaded to MotherDuck.")

def download_link(df, filename):
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    st.download_button(label=f"📥 Download {filename}.csv", data=towrite.getvalue(), file_name=f"{filename}.csv", mime="text/csv")

# --- Generate Data ---
if st.session_state['regen']:
    df_portfolio = generate_portfolio_data()
    df_transactions = generate_transaction_data()
    df_budget = generate_budget_data()
    df_actions = generate_corporate_actions()
    df_flows = generate_investor_flows()
    df_aml = generate_aml_data()
    df_register = generate_investor_register()
    df_servicing = calculate_servicing_cost(df_portfolio)
    df_admin_cost = calculate_admin_costs(df_portfolio)
    st.session_state['regen'] = False

# --- UI Tabs ---
tabs = st.tabs(["Portfolio", "Transactions", "Budget", "Corp Actions", "Investor Flows", "AML", "Register", "Servicing Cost", "Admin Cost"])
with tabs[0]:
    st.dataframe(df_portfolio)
    fig = px.pie(df_portfolio, names="asset_type", values="market_value", title="Asset Type Allocation")
    st.plotly_chart(fig)
    download_link(df_portfolio, "portfolio")
with tabs[1]: st.dataframe(df_transactions); download_link(df_transactions, "transactions")
with tabs[2]: st.dataframe(df_budget); download_link(df_budget, "budget")
with tabs[3]: st.dataframe(df_actions); download_link(df_actions, "corporate_actions")
with tabs[4]: st.dataframe(df_flows); download_link(df_flows, "investor_flows")
with tabs[5]: st.dataframe(df_aml); download_link(df_aml, "aml")
with tabs[6]: st.dataframe(df_register); download_link(df_register, "investor_register")
with tabs[7]: st.dataframe(df_servicing); download_link(df_servicing, "servicing_cost")
with tabs[8]: st.dataframe(df_admin_cost); download_link(df_admin_cost, "admin_cost")

if st.sidebar.button("📤 Upload to MotherDuck"):
    send_to_motherduck({
        "portfolio": df_portfolio,
        "transactions": df_transactions,
        "budget": df_budget,
        "corp_actions": df_actions,
        "flows": df_flows,
        "aml": df_aml,
        "register": df_register,
        "servicing_cost": df_servicing,
        "admin_cost": df_admin_cost
    })
