import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Streamlit app title
st.title("Inbound vs OOS Analysis")


inb_df = pd.read_csv("inb.csv")
total_df = pd.read_csv("total.csv")
analisa_df = pd.read_csv("analisa.csv")

# Ensure date columns are in datetime format
inb_df['Date'] = pd.to_datetime(inb_df['Date'])
total_df['Date'] = pd.to_datetime(total_df['Date'])
analisa_df['Inbound_Date NEW'] = pd.to_datetime(analisa_df['Inbound_Date NEW'])

# Adjust inbound dates to align with OOS dates (OOS dates = Inb dates +2)
inb_df['OOS_Date'] = inb_df['Date'] + pd.Timedelta(days=2)

    # Merge inbound data with total data on adjusted OOS dates
merged_df = pd.merge(total_df, inb_df[['Date','OOS_Date', 'Actual', 'Max Projected']],
                         left_on='Date', right_on='OOS_Date', how='left')

# Calculate projected OOS% based on inbound quantity ratio
#st.write("Analisa Data Columns:", analisa_df.columns)
#analisa_df.columns = analisa_df.columns.str.strip()
merged_df['Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])
#merged_df = pd.merge(merged_df, analisa_df, left_on='Date', right_on='Inbound_Date NEW', how='left')

# Display data
#st.subheader("Merged Data Preview")
#st.write(merged_df[['Date', 'Actual', 'Max Projected', '% OOS Contribution', 'Projected % OOS Contribution']].head())

    # Plot actual vs projected inbound quantity
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(inb_df['Date'], merged_df['Actual'], label='Actual Inb Qty', marker='o')
ax.plot(inb_df['Date'], merged_df['Max Projected'], label='Projected Inb Qty', marker='s')
ax.set_xlabel('Date')
ax.set_ylabel('Inbound Quantity')
ax.set_title('Actual vs Projected Inbound Quantity')
ax.legend()
ax.grid()
st.pyplot(fig)

    # Plot actual vs projected OOS% trend
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(merged_df['OOS_Date'], merged_df['% OOS Contribution'], label='Actual OOS %', marker='d', color='r')
ax.plot(merged_df['OOS_Date'], merged_df['Projected % OOS Contribution'], label='Projected OOS %', marker='x', color='b')
ax.set_xlabel('Date')
ax.set_ylabel('OOS %')
ax.set_title('Actual vs Projected Out-of-Stock Percentage Trend')
ax.legend()
ax.grid()
st.pyplot(fig)

# Product ID filter
product_ids = analisa_df['product_id'].unique()
selected_product = st.selectbox("Select Product ID", product_ids)
filtered_df = analisa_df[analisa_df['product_id'] == selected_product]

filtered_df[['Landed DOI New', 'Landed DOI OLD']] = filtered_df[['Landed DOI New', 'Landed DOI OLD']].astype(float)
filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].astype(float)

#fig, ax = plt.subplots(figsize=(10, 5))
#ax.barh(['Landed DOI New', 'Landed DOI OLD'], [filtered_df['Landed DOI New'].mean(), filtered_df['Landed DOI OLD'].mean()], color=['r', 'g'])
#ax.set_xlabel('Landed DOI')
#ax.set_title('Comparison of Landed DOI New vs Old')
#ax.grid()
#st.pyplot(fig)

#fig, ax = plt.subplots(figsize=(9, 5))
#ax.barh(['RL Qty Actual', 'RL Qty NEW after MIN QTY WH'], [filtered_df['RL Qty Actual'].mean(), filtered_df['RL Qty NEW after MIN QTY WH'].mean()], color=['r', 'g'])
#ax.set_xlabel('RL Quantity')
#ax.set_title('Comparison of RL Qty')
#ax.grid()
#st.pyplot(fig)

import plotly.express as px

# Landed DOI Comparison
landed_doi_data = pd.DataFrame({
    "Category": ["Landed DOI New", "Landed DOI Old"],
    "Value": [filtered_df['Landed DOI New'].mean(), filtered_df['Landed DOI OLD'].mean()]
})

fig_doi = px.bar(landed_doi_data, x="Value", y="Category", orientation='h',
                 title="Comparison of Landed DOI New vs Old", color="Category",
                 color_discrete_map={"Landed DOI New": "red", "Landed DOI Old": "green"})

st.plotly_chart(fig_doi)

# RL Quantity Comparison
rl_qty_data = pd.DataFrame({
    "Category": ["RL Qty Actual", "RL Qty NEW after MIN QTY WH"],
    "Value": [filtered_df['RL Qty Actual'].mean(), filtered_df['RL Qty NEW after MIN QTY WH'].mean()]
})

fig_rl = px.bar(rl_qty_data, x="Value", y="Category", orientation='h',
                title="Comparison of RL Qty", color="Category",
                color_discrete_map={"RL Qty Actual": "red", "RL Qty NEW after MIN QTY WH": "green"})

st.plotly_chart(fig_rl)
