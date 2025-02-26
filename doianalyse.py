import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Streamlit app title
st.title("Inbound vs OOS Analysis")

# Load CSV files
inb_df = pd.read_csv("inb.csv")
total_df = pd.read_csv("total.csv")
analisa_df = pd.read_csv("analisa.csv")

# Ensure date columns are in datetime format
inb_df['Date'] = pd.to_datetime(inb_df['Date']).dt.date
total_df['Date'] = pd.to_datetime(total_df['Date']).dt.date
analisa_df['Inbound_Date NEW'] = pd.to_datetime(analisa_df['Inbound_Date NEW']).dt.date

# Adjust inbound dates to align with OOS dates (OOS dates = Inb dates +2)
inb_df['OOS_Date'] = inb_df['Date'] + pd.Timedelta(days=2)

# Merge inbound data with total data on adjusted OOS dates
merged_df = pd.merge(total_df, inb_df[['Date', 'OOS_Date', 'Actual', 'Max Projected']],
                     left_on='Date', right_on='OOS_Date', how='left')

# Calculate projected OOS% based on inbound quantity ratio
merged_df['Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])
merged_df2 = merged_df[['Date_y', 'Actual', 'Max Projected', '% OOS Contribution', 'Projected % OOS Contribution']]
merged_df2.rename(columns={'Date_y': 'Date'}, inplace=True) 
merged_df2 = merged_df2.sort_values(by='Date', ascending=True)
st.data_editor(merged_df2, hide_index=True)



analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].apply(pd.to_numeric, errors='coerce')
analisa_df['Landed DOI New'] = analisa_df['Landed DOI New'].fillna(0)
analisa_df['Landed DOI OLD'] = analisa_df['Landed DOI OLD'].fillna(0)
analisa_df[['Landed DOI New', 'Landed DOI OLD']] = analisa_df[['Landed DOI New', 'Landed DOI OLD']].apply(pd.to_numeric, errors='coerce')

analisa_df['RL Qty Actual'] = analisa_df['RL Qty Actual'].fillna(0)
analisa_df['RL Qty NEW after MIN QTY WH'] = analisa_df['RL Qty NEW after MIN QTY WH'].fillna(0)

filtered_df1 = analisa_df[(analisa_df['RL Qty Actual'] == 0) & (analisa_df['RL Qty NEW after MIN QTY WH'] != 0)][['product_id', 'RL Qty Actual', 'RL Qty NEW after MIN QTY WH']]

# Calculate summary statistics
total_products = filtered_df1['product_id'].nunique()  # Count unique products
total_rl_qty_new = filtered_df1['RL Qty NEW after MIN QTY WH'].sum().astype(int)  # Sum of RL Qty NEW

# Display the table without an index
st.data_editor(filtered_df1, hide_index=True)

# Show summary at the bottom
st.write(f"**Total Count SKUs with prevented OOS (ke order sebelumnya tidak):** {total_products}")
st.write(f"**Total Sum of RL Qty New DOI Policy:** {total_rl_qty_new}")

# Plot actual vs projected inbound quantity

fig_inb = px.bar(inb_df, x='Date', y=['Actual', 'Max Projected'],
                 labels={'value': 'Inbound Quantity', 'variable': 'Type'},
                 title='Actual vs Projected Inbound Quantity',
                 barmode='group')

# Create the OOS percentage line chart
fig_oos = px.line(merged_df, x='OOS_Date', y=['% OOS Contribution', 'Projected % OOS Contribution'],
                  labels={'value': 'OOS %', 'variable': 'Type'},
                  title='Actual vs Projected Out-of-Stock Percentage Trend')

# Selectbox for choosing which chart to display
chart_option = st.selectbox("Select a graph to display:", ["Inbound Quantity", "Out-of-Stock Percentage"])

# Display the selected chart
if chart_option == "Inbound Quantity":
    st.plotly_chart(fig_inb)
else:
    st.plotly_chart(fig_oos)


# Exclude Landed DOI values greater than 21 before calculating the average
selected_locations = st.multiselect("Select Location(s):", analisa_df['Location_ID'].unique())

# Filter the DataFrame based on selected locations
if selected_locations:
    filtered_df = analisa_df[analisa_df['Location_ID'].isin(selected_locations)]
else:
    filtered_df = analisa_df  # If no selection, show all data

# Apply the DOI filtering
filtered_doi_df = filtered_df[filtered_df['Landed DOI New'] <= 21]
filtered_doi_old_df = filtered_df[filtered_df['Landed DOI OLD'] <= 21]

# Calculate averages
avg_landed_doi_new = filtered_doi_df['Landed DOI New'].mean()
avg_landed_doi_old = filtered_doi_old_df['Landed DOI OLD'].mean()

# Display results with 2 decimal places
st.write(f"**Average Landed DOI New:** {avg_landed_doi_new:.2f}")
st.write(f"**Average Landed DOI OLD:** {avg_landed_doi_old:.2f}")

# Product ID filter
product_ids = analisa_df['product_id'].unique()
selected_product = st.selectbox("Select Product ID", product_ids)
filtered_df = analisa_df[analisa_df['product_id'] == selected_product]


filtered_df['Landed DOI New'] = filtered_df['Landed DOI New'].fillna(0)
filtered_df['Landed DOI OLD'] = filtered_df['Landed DOI OLD'].fillna(0)
filtered_df['RL Qty NEW after MIN QTY WH'] = filtered_df['RL Qty NEW after MIN QTY WH'].fillna(0)
filtered_df[['Landed DOI New', 'Landed DOI OLD']] = filtered_df[['Landed DOI New', 'Landed DOI OLD']].astype(float)
filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].astype(float)

# Landed DOI Comparison
landed_doi_data = pd.DataFrame({
    "Category": ["Landed DOI New", "Landed DOI Old"],
    "Value": [filtered_df['Landed DOI New'].mean(), filtered_df['Landed DOI OLD'].mean()]
})

fig_doi = px.bar(landed_doi_data, x="Value", y="Category", orientation='h',
                 title="Comparison of Landed DOI New vs Old", color="Category",
                 color_discrete_map={"Landed DOI New": "green", "Landed DOI Old": "red"})

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


