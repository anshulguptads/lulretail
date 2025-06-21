import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config("Lulu Retail MVP", layout="wide", page_icon="🛒")
st.title("Lulu Hypermarket - Retail MVP Dashboard")

st.markdown("""
<style>
    .stMetricValue { color: #003366 !important; }
    .stMetricLabel { color: #336699 !important; }
</style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df_products = pd.read_csv("products_master.csv")
    df_stores = pd.read_csv("stores_master.csv")
    df_calendar = pd.read_csv("calendar_master.csv")
    df_inventory = pd.read_csv("inventory_transactions.csv")
    df_sales = pd.read_csv("sales_transactions.csv")
    return df_products, df_stores, df_calendar, df_inventory, df_sales

df_products, df_stores, df_calendar, df_inventory, df_sales = load_data()

# ---- KPIs ----
total_sales = df_sales['Net_Sales_AED'].sum()
total_units = df_sales['Units_Sold'].sum()
unique_skus = df_sales['Product_ID'].nunique()
stores_count = df_sales['Store_ID'].nunique()
promo_sales = df_sales[df_sales['Promotion_Flag'] == 'Y']['Net_Sales_AED'].sum()
promo_pct = (promo_sales / total_sales * 100) if total_sales > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Net Sales (AED)", f"{total_sales:,.0f}")
col2.metric("Total Units Sold", f"{total_units:,}")
col3.metric("Active SKUs", unique_skus)
col4.metric("Stores", stores_count)
col5.metric("Sales on Promotion (%)", f"{promo_pct:.1f}")

# ---- Top SKUs ----
st.subheader("Top 10 SKUs by Net Sales")
top_skus = df_sales.groupby('Product_ID')['Net_Sales_AED'].sum().reset_index().sort_values('Net_Sales_AED', ascending=False).head(10)
top_skus = top_skus.merge(df_products[['Product_ID', 'Product_Name']], on='Product_ID', how='left')

fig1, ax1 = plt.subplots(figsize=(8, 5))
ax1.bar(top_skus['Product_Name'], top_skus['Net_Sales_AED'], color="#1976D2")
ax1.set_xlabel('SKU')
ax1.set_ylabel('Net Sales (AED)')
ax1.set_title('Top 10 SKUs by Net Sales')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

# ---- Net Sales Trend ----
st.subheader("Total Net Sales Trend")
df_sales['Date'] = pd.to_datetime(df_sales['Date'])
sales_trend = df_sales.groupby('Date')['Net_Sales_AED'].sum().reset_index()

fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.plot(sales_trend['Date'], sales_trend['Net_Sales_AED'], marker='o', color="#388E3C")
ax2.set_xlabel('Date')
ax2.set_ylabel('Net Sales (AED)')
ax2.set_title('Net Sales Over Time')
plt.xticks(rotation=45)
st.pyplot(fig2)

# ---- Category Share ----
st.subheader("Category-wise Net Sales Distribution")
cat_sales = df_sales.merge(df_products[['Product_ID','Category']], on='Product_ID', how='left')
cat_summary = cat_sales.groupby('Category')['Net_Sales_AED'].sum().sort_values(ascending=False)

fig3, ax3 = plt.subplots(figsize=(7, 5))
ax3.pie(cat_summary, labels=cat_summary.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
ax3.set_title('Net Sales Share by Category')
st.pyplot(fig3)

# ---- Inventory Overview ----
st.subheader("Closing Stock by Store (Sample of Top 5)")
inv_summary = df_inventory.groupby('Store_ID')['Closing_Stock'].sum().reset_index()
inv_summary = inv_summary.merge(df_stores[['Store_ID', 'Store_Name']], on='Store_ID', how='left')
inv_top5 = inv_summary.sort_values('Closing_Stock', ascending=False).head(5)

fig4, ax4 = plt.subplots(figsize=(8, 5))
ax4.bar(inv_top5['Store_Name'], inv_top5['Closing_Stock'], color="#FFA000")
ax4.set_xlabel('Store')
ax4.set_ylabel('Closing Stock (Total Units)')
ax4.set_title('Top 5 Stores by Closing Stock')
plt.xticks(rotation=20)
st.pyplot(fig4)

# ---- Show Raw Data Option ----
with st.expander("Show Raw Sales Data (first 500 rows)"):
    st.dataframe(df_sales.head(500))

with st.expander("Show Raw Inventory Data (first 500 rows)"):
    st.dataframe(df_inventory.head(500))

st.markdown("""
---
<b>MVP Dashboard - Lulu Hypermarket | Retail Analytics</b>
""", unsafe_allow_html=True)

