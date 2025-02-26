import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Load the data
inb_df = pd.read_csv("inb.csv")
total_df = pd.read_csv("total.csv")
analisa_df = pd.read_csv("analisa.csv")

# Display the first few rows to understand the structure
print("Inbound Data:")
print(inb_df.head())
print("\nTotal Data:")
print(total_df.head())

# Ensure date columns are in datetime format
inb_df['Date'] = pd.to_datetime(inb_df['Date'])
total_df['Date'] = pd.to_datetime(total_df['Date'])

# Adjust inbound dates to align with OOS dates (OOS dates = Inb dates +2)
inb_df['OOS_Date'] = inb_df['Date'] + pd.Timedelta(days=2)

# Merge inbound data with total data on adjusted OOS dates
merged_df = pd.merge(total_df, inb_df[['OOS_Date', 'Actual', 'Max Projected']],
                     left_on='Date', right_on='OOS_Date', how='left')

# Filter projected OOS% calculations for 12 Feb - 17 Feb
#projection_dates = (merged_df['Date'] >= '2025-02-10') & (merged_df['Date'] <= '2025-02-15')
merged_df[ 'Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])


# Merge the datasets if necessary (assuming 'Date' is the key column)
#merged_df = pd.merge(inb_df, total_df, on='Date', how='inner')

# Calculate projected OOS% based on inbound quantity ratio
#merged_df['Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])

# Plot actual vs projected inb qty
plt.figure(figsize=(10, 5))
plt.plot(merged_df['Date'], merged_df['Actual'], label='Actual Inb Qty', marker='o')
plt.plot(merged_df['Date'], merged_df['Max Projected'], label='Projected Inb Qty', marker='s')
plt.xlabel('Date')
plt.ylabel('Inbound Quantity')
plt.title('Actual vs Projected Inbound Quantity')
plt.legend()
plt.grid()
plt.show()

# Plot actual vs projected OOS% trend
plt.figure(figsize=(10, 5))
plt.plot(merged_df['Date'], merged_df['% OOS Contribution'], label='Actual OOS %', marker='d', color='r')
plt.plot(merged_df['Date'], merged_df['Projected % OOS Contribution'], label='Projected OOS %', marker='x', color='b')
plt.xlabel('Date')
plt.ylabel('OOS %')
plt.title('Actual vs Projected Out-of-Stock Percentage Trend')
plt.legend()
plt.grid()
plt.show()

# Bar plot for inbound quantities

# Plot inbound quantities as bar charts and overlay OOS% as lines
fig, ax1 = plt.subplots(figsize=(10, 5))

bar_width = 0.4
x_indexes = np.arange(len(merged_df['Date']))
ax1.bar(x_indexes - bar_width/2, merged_df['Actual'], width=bar_width, label='Actual Inb Qty', alpha=0.7)
ax1.bar(x_indexes + bar_width/2, merged_df['Max Projected'], width=bar_width, label='Projected Inb Qty', alpha=0.7)
ax1.set_xlabel('Date')
ax1.set_ylabel('Inbound Quantity')
ax1.set_xticks(x_indexes)
ax1.set_xticklabels(merged_df['Date'].dt.strftime('%Y-%m-%d'), rotation=45)
ax1.legend(loc='upper left')
ax1.grid(axis='y')

# Line plot for OOS%
ax2 = ax1.twinx()
ax2.plot(x_indexes, merged_df['% OOS Contribution'], label='Actual OOS %', marker='d', color='r', linestyle='--')
ax2.plot(x_indexes, merged_df['Projected % OOS Contribution'], label='Projected OOS %', marker='x', color='b', linestyle='--')
ax2.set_ylabel('OOS %')
ax2.legend(loc='upper right')

plt.title('Inbound Quantity and OOS% Trend')
plt.show()


st.title("Inbound Quantity and OOS Analysis")

# Display dataset preview
st.subheader("Data Preview")
st.write(merged_df.head())

# Compare RL Qty, Actual RL Qty, NEW Landed DOI, OLD Landed DOI for each Product ID
st.subheader("Comparison of RL Qty, Actual RL Qty, Landed DOI OLD, and Landed DOI NEW")
selected_product = st.selectbox("Select Product ID", merged_df['Product ID'].unique())
filtered_data = merged_df[merged_df['Product ID'] == selected_product]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(filtered_data['Date'], filtered_data['New_RL_Qty'], label='RL Qty', marker='o')
ax.plot(filtered_data['Date'], filtered_data['RL Qty Actual'], label='Actual RL Qty', marker='s')
ax.plot(filtered_data['Date'], filtered_data['Landed DOI OLD'], label='Landed DOI OLD', marker='d')
ax.plot(filtered_data['Date'], filtered_data['Landed DOI New'], label='Landed DOI New', marker='x')

ax.set_xlabel('Date')
ax.set_ylabel('Quantity / DOI')
ax.set_title(f'Comparison for Product ID: {selected_product}')
ax.legend()
ax.grid()
st.pyplot(fig)

# Average Landed DOI comparison by Location ID
st.subheader("Average Landed DOI by Location ID")
avg_doi = merged_df.groupby('Location ID')[['Landed DOI OLD', 'Landed DOI New']].mean()
st.write(avg_doi)
