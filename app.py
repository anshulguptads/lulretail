# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Lulu Retail Analytics", layout="wide")

@st.cache_data
def load_data():
    return (
        pd.read_csv("products_master.csv"),
        pd.read_csv("stores_master.csv"),
        pd.read_csv("calendar_master.csv"),
        pd.read_csv("inventory_transactions.csv"),
        pd.read_csv("sales_transactions.csv")
    )
df_prod, df_store, df_cal, df_inv, df_sales = load_data()
df_sales['Date'] = pd.to_datetime(df_sales['Date'])
df_inv['Date'] = pd.to_datetime(df_inv['Date'])

tabs = st.tabs(["Overview", "Sales", "Inventory", "Forecasting", "Raw Data"])

# --- Overview Tab ---
with tabs[0]:
    st.header("Executive Overview")
    total_sales = df_sales['Net_Sales_AED'].sum()
    total_units = df_sales['Units_Sold'].sum()
    promo_pct = df_sales[df_sales['Promotion_Flag']=='Y']['Net_Sales_AED'].sum() / total_sales * 100
    st.metric("Net Sales (AED)", f"{total_sales:,.0f}")
    st.metric("Units Sold", f"{total_units:,}")
    st.metric("Promo Sales %", f"{promo_pct:.1f}%")
    top_sku = df_sales.groupby('Product_ID')['Net_Sales_AED'].sum().nlargest(5)
    st.write("**Top 5 SKUs**")
    st.write(top_sku.reset_index().merge(df_prod, on='Product_ID')[['Product_Name','Net_Sales_AED']])

# --- Sales Analytics Tab ---
with tabs[1]:
    st.header("Sales Analytics")
    grp = st.sidebar.multiselect("Category", df_prod['Category'].unique(), default=df_prod['Category'].unique())
    sel = df_sales[df_sales['Product_ID'].isin(df_prod[df_prod['Category'].isin(grp)]['Product_ID'])]
    st.subheader("Monthly Sales Trend")
    monthly = sel.groupby(sel['Date'].dt.to_period('M'))['Net_Sales_AED'].sum().reset_index()
    monthly['Date'] = monthly['Date'].dt.to_timestamp()
    plt.figure(figsize=(8,4))
    sns.lineplot(data=monthly, x='Date', y='Net_Sales_AED', marker='o')
    plt.title("Net Sales by Month")
    st.pyplot(plt.gcf())

    st.subheader("Category Heatmap")
    cat_month = sel.assign(Month=sel['Date'].dt.month).groupby(['Category','Month'])['Net_Sales_AED'].sum().unstack()
    plt.figure(figsize=(8,4))
    sns.heatmap(cat_month, annot=True, fmt=".0f", cmap="YlGnBu")
    st.pyplot(plt.gcf())

# --- Inventory Analytics Tab ---
with tabs[2]:
    st.header("Inventory Analytics")
    st.subheader("Stock by Store")
    inv_sum = df_inv.groupby('Store_ID')['Closing_Stock'].sum().nlargest(5).reset_index()
    inv_sum = inv_sum.merge(df_store, on='Store_ID')
    plt.figure(figsize=(6,3))
    sns.barplot(data=inv_sum, y='Store_Name', x='Closing_Stock', palette="Oranges_r")
    st.pyplot(plt.gcf())

    st.subheader("Stock-Out Frequency")
    so = df_inv[df_inv['Closing_Stock']==0].groupby('Store_ID')['Date'].count().reset_index()
    so = so.merge(df_store, on='Store_ID')
    plt.figure(figsize=(6,3))
    sns.barplot(data=so, y='Store_Name', x='Date', palette="Reds_r")
    st.pyplot(plt.gcf())

# --- Forecasting Tab ---
with tabs[3]:
    st.header("Basic Forecasting with Prophet")
    sku = st.selectbox("Select SKU", df_prod['Product_ID'])
    sku_data = df_sales[df_sales['Product_ID']==sku].groupby('Date')['Units_Sold'].sum().reset_index().rename(columns={'Date':'ds','Units_Sold':'y'})
    if len(sku_data) >= 30:
        m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
        m.fit(sku_data)
        future = m.make_future_dataframe(periods=30)
        fc = m.predict(future)
        fig = m.plot(fc)
        st.pyplot(fig)
        st.write("Forecast Table:", fc[['ds','yhat','yhat_lower','yhat_upper']].tail(5))
    else:
        st.info("Need at least 30 days of data for meaningful forecast.")

# --- Raw Data Tab ---
with tabs[4]:
    st.header("Raw Datasets")
    st.write("**Sales**")
    st.dataframe(df_sales.head(500))
    st.write("**Inventory**")
    st.dataframe(df_inv.head(500))
