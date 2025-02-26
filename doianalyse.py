import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Streamlit app title
st.markdown("<h1 style='color: maroon;'>Why use L2PO for DOI Policy?</h1>", unsafe_allow_html=True)
st.subheader("Overall View")
st.markdown(" ")

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
col1, col2 = st.columns([1, 3])
with col2:
  st.data_editor(merged_df2, hide_index=True, use_container_width = True)
with col1:
    # Text area for notes
    notes = """
    **Background:**  
    - Data is from cycle 3-6 Feb RL Upload -> Inbound 10-15 Feb.  
    - Assume 2 days buffer SO -> OOS reflected 2 days post Inbound.
    Used Logic: DOI Policy 5 days, No Min SS WH, Cov 14 days
    Proposed Logic: DOI Policy L2PO, With Min SS WH, Cov Next Next Inb
    """
    st.markdown(notes)



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
st.markdown("----")
st.markdown("Below are the list of SKUs that we **did not** order but **would order** with new doi policy:")
col1, col2 = st.columns([2, 2])
with col1:
  st.data_editor(filtered_df1, hide_index=True, use_container_width= False)
with col2:
     # Text area for notes
    notes = """
    - Used Logic: DOI Policy 5 days, No Min SS WH, Cov 14 days
    - Proposed Logic: DOI Policy L2PO, With Min SS WH, Cov Next Next Inb
    """
    st.markdown(notes)
    st.write(f"**Count SKUs with potential in preventing OOS occurences:** {total_products}")
    st.write(f"**Sum of Add. RL Qty with New DOI Policy:** {total_rl_qty_new}")
    


# Show summary at the bottom


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

st.markdown("----")
# Exclude Landed DOI values greater than 21 before calculating the average
col1, col2 = st.columns(2)

# Multiselect filters
with col1:
    selected_locations = st.multiselect("Select Location(s):", analisa_df['location_id'].unique())

with col2:
    selected_categories = st.selectbox("Select L1 Category(s):", analisa_df['l1_category_name'].unique())

# Apply filtering based on selections
filtered_df = analisa_df.copy()  # Start with full DataFrame

if selected_locations:
    filtered_df = filtered_df[filtered_df['location_id'].isin(selected_locations)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['l1_category_name'] == selected_categories]

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
analisa_df["product_display"] = analisa_df["product_id"].astype(str) + " - " + analisa_df["product_name"]

# Create a dictionary to map the display name back to the Product ID
product_map = dict(zip(analisa_df["product_display"], analisa_df["product_id"]))

# Selectbox with formatted product ID and name
selected_product_display = st.selectbox("Select Product", list(product_map.keys()))

# Filter the dataframe using the actual Product ID
selected_product_id = product_map[selected_product_display]
filtered_df = analisa_df[analisa_df['product_id'] == selected_product_id]


filtered_df['Landed DOI New'] = filtered_df['Landed DOI New'].fillna(0)
filtered_df['Landed DOI OLD'] = filtered_df['Landed DOI OLD'].fillna(0)
filtered_df['RL Qty NEW after MIN QTY WH'] = filtered_df['RL Qty NEW after MIN QTY WH'].fillna(0)
filtered_df[['Landed DOI New', 'Landed DOI OLD']] = filtered_df[['Landed DOI New', 'Landed DOI OLD']].astype(float)
filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = filtered_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].astype(float)

# Landed DOI Comparison
col1, col2 = st.columns(2)

# Landed DOI Comparison
with col1:
    landed_doi_data = pd.DataFrame({
        "Category": ["Landed DOI New", "Landed DOI Old"],
        "Value": [filtered_df['Landed DOI New'].mean(), filtered_df['Landed DOI OLD'].mean()]
    })

    fig_doi = px.bar(landed_doi_data, y="Value", x="Category", orientation='v',
                     title="Comparison of Landed DOI New vs Old", color="Category",
                     color_discrete_map={"Landed DOI New": "green", "Landed DOI Old": "red"})

    st.plotly_chart(fig_doi, use_container_width=True)

# RL Quantity Comparison
with col2:
    rl_qty_data = pd.DataFrame({
        "Category": ["RL Qty Actual", "RL Qty NEW after MIN QTY WH"],
        "Value": [filtered_df['RL Qty Actual'].mean(), filtered_df['RL Qty NEW after MIN QTY WH'].mean()]
    })

    fig_rl = px.bar(rl_qty_data, y="Value", x="Category", orientation='v',
                    title="Comparison of RL Qty", color="Category",
                    color_discrete_map={"RL Qty Actual": "red", "RL Qty NEW after MIN QTY WH": "green"})

    st.plotly_chart(fig_rl, use_container_width=True)


