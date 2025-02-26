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
st.write("Analisa Data Columns:", analisa_df.columns)

merged_df['Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])
merged_df = pd.merge(merged_df, analisa_df, left_on='Date', right_on='Inbound_Date NEW', how='left')

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

# Compare RL Qty Actual vs RL Qty New after MIN QTY WH
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(merged_df['Inbound_Date NEW'], merged_df['RL Qty Actual'], label='RL Qty Actual', marker='o', color='b')
ax.plot(merged_df['Inbound_Date NEW'], merged_df['RL Qty New after MIN QTY WH'], label='RL Qty New after MIN QTY WH', marker='s', color='m')
ax.set_xlabel('Date')
ax.set_ylabel('RL Quantity')
ax.set_title('RL Qty Actual vs RL Qty New after MIN QTY WH')
ax.legend()
ax.grid()
st.pyplot(fig)

