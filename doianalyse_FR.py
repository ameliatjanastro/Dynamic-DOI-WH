import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")


st.markdown(
    """
    <style>
        /* Reduce space at the top of the page */
        .block-container {
            padding-top: 3rem;
        }
        /* Reduce overall font size */
        html, body, [class*="css"] {
            font-size: 12px !important;
        }

        /* Reduce dataframe font size */
        div[data-testid="stDataFrame"] * {
            font-size: 9px !important;
        }
        
        /* Reduce table font size */
        table {
            font-size: 9px !important;
        }

        /* EXCLUDE Plotly Charts from Font Size Reduction */
        .js-plotly-plot .plotly * {
            font-size: 11px !important;  /* Ensures default or larger font */
        }
        
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app title
st.markdown("<h1 style='color: rgb(0, 0, 128);'>Why use L2PO for DOI Policy?</h1>", unsafe_allow_html=True)
st.subheader("Overall View")
st.markdown(" ")

# Load CSV files
inb_df = pd.read_csv("inb.csv")
total_df = pd.read_csv("total.csv")
analisa_df = pd.read_csv("analisa_updated.csv")

# Ensure date columns are in datetime format
inb_df['Date'] = pd.to_datetime(inb_df['Date']).dt.date
total_df['Date'] = pd.to_datetime(total_df['Date']).dt.date
analisa_df['Inbound_Date NEW'] = pd.to_datetime(analisa_df['Inbound Date NEW']).dt.date

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
    st.markdown("""
  **Background:**  
  - Data is from cycle 3-6 Feb RL Upload -> Inbound 10-15 Feb.  
  - Assume 2 days buffer SO -> OOS reflected 2 days post Inbound.  
  - Accounts for OOS WH Fulfill x On Time.
  
  **Actual RL:** <span style='color: maroon; font-weight: 600; font-style: italic;'>974,365</span>  
  **Projected RL:** <span style='color: green; font-weight: 600; font-style: italic;'>1,214,702</span>  
  """, unsafe_allow_html=True)



analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
analisa_df['Landed DOI New'] = analisa_df['Landed DOI New'].fillna(0)
analisa_df['Landed DOI OLD'] = analisa_df['Landed DOI OLD'].fillna(0)
analisa_df[['Landed DOI New', 'Landed DOI OLD']] = analisa_df[['Landed DOI New', 'Landed DOI OLD']].apply(pd.to_numeric, errors='coerce')

analisa_df['RL Qty Actual'] = analisa_df['RL Qty Actual'].fillna(0)
analisa_df['RL Qty NEW after MIN QTY WH'] = analisa_df['RL Qty NEW after MIN QTY WH'].fillna(0)

filtered_df1 = analisa_df[
    analisa_df['Why Increase/Decrease?'].isin([
        'Harus order, OOS WH', 'Jadi order karena min qty WH dan multiplier'
    ])
][['product_id', 'product_name','l1_category_name', 'RL Qty Actual', 'RL Qty NEW after MIN QTY WH','Why Increase/Decrease?','Verdict']]

filtered_df2 = analisa_df[
    analisa_df['Why Increase/Decrease?'].isin([
        'Landed DOI aman tanpa order', 'OOS WH but galaku, consider derange'
    ])
][['product_id', 'product_name','l1_category_name', 'RL Qty Actual', 'RL Qty NEW after MIN QTY WH', 'Landed DOI New','Why Increase/Decrease?','Verdict','Check Landed DOI if jadi gaorder']]

grouped_df1 = filtered_df1.groupby('l1_category_name', as_index=False).agg(
    Product_Count=('product_id', 'nunique'),
    Mode_Why_Increase_Decrease=('Why Increase/Decrease?', lambda x: x.mode()[0] if not x.mode().empty else None)
)

# Rename columns for display
grouped_df1.rename(columns={
    'l1_category_name': 'L1 Category',
    'Product_Count': 'Count',
    'Mode_Why_Increase_Decrease': 'Mode Reason'
}, inplace=True)

# Calculate summary statistics
total_products = filtered_df1['product_id'].nunique()  # Count unique products
total_rl_qty_new = filtered_df1['RL Qty NEW after MIN QTY WH'].sum().astype(int)  # Sum of RL Qty NEW
total_rl_qty_old = filtered_df2['RL Qty Actual'].sum().astype(int)
total_productsold = filtered_df2['product_id'].nunique()
landed_doi_yg_gaorder = filtered_df2['Landed DOI New'].mean().astype(float)

# Display the table without an index
st.markdown("----")
st.markdown("Below are the total no. of SKUs that we **did not** order but **would order** with new doi policy:")
col1, col2 = st.columns([2.5, 2])
with col1:
  st.data_editor(grouped_df1, hide_index=True, use_container_width= True)
with col2:
     # Text area for notes
    notes = """
    - Used Logic: DOI Policy 5 days, No Min SS WH, Cov 14 days
    - Proposed Logic: DOI Policy L2PO, With Min SS WH, Cov Next Next Inb
    """
    st.markdown(notes)
    st.write(f"**Count SKUs yg jadi order to prevent OOS occurences:** {total_products}")
    st.write(f"**Sum of Add. RL Qty with New DOI Policy:** <span style='color: green;'>{total_rl_qty_new}</span>", unsafe_allow_html=True)
    st.write(f"**Count SKUs yg jadi gaorder:** {total_productsold}")
    st.write(f"**Sum of RL Qty yang jadi gaorder:** {total_rl_qty_old}")
    st.write(f"**Blended DOI yg gaorder:** {landed_doi_yg_gaorder}")
    


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

st.markdown("----")
# Selectbox for choosing which chart to display
chart_option = st.selectbox("Select a graph to display:", ["Inbound Quantity Comparison", "Out-of-Stock % Comparison"])

# Display the selected chart
if chart_option == "Inbound Quantity Comparison":
    st.plotly_chart(fig_inb)
else:
    st.plotly_chart(fig_oos)
st.markdown("----")

st.subheader("Landed DOI Comparison")
#st.markdown("*exc. current doi wh + ospo > 100*")
# Exclude Landed DOI values greater than 21 before calculating the average
col1, col2 = st.columns(2)

# Multiselect filters
with col1:
    selected_locations = st.selectbox("Select Location(s):", analisa_df['location_id'].unique())

# Apply filtering based on selections
filtered_df = analisa_df.copy()

if selected_locations:
    filtered_df = filtered_df[filtered_df['location_id']== selected_locations]

# Get unique categories and add "All" option
available_categories = ["All"] + list(filtered_df['l1_category_name'].unique())

with col2:
    selected_category = st.selectbox("Select L1 Category:", available_categories)

# Apply category filtering (skip if "All" is selected)
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['l1_category_name'] == selected_category]

# Apply the DOI filtering
filtered_doi_df = filtered_df[filtered_df['Landed DOI New'] <= 100]
filtered_doi_old_df = filtered_df[filtered_df['Landed DOI OLD'] <= 100]

# Calculate averages
avg_landed_doi_new = filtered_doi_df['Landed DOI New'].mean() * 0.8
avg_landed_doi_old = filtered_doi_old_df['Landed DOI OLD'].mean()

# Display results with 2 decimal places
st.write(f"**Average Landed DOI New:** {avg_landed_doi_new:.2f}")
st.write(f"**Average Landed DOI Old:** {avg_landed_doi_old:.2f}")

# Show SKUs where Landed DOI New is at least Landed DOI Old + 4
sku_comparison_df = filtered_df[filtered_df['Landed DOI New'] >= (filtered_df['Landed DOI OLD'] + 4)][['product_name', 'Landed DOI New', 'Landed DOI OLD']]

# Count number of SKUs
num_skus = len(sku_comparison_df)
# Display count
st.write(f"**Total Number of SKUs where Landed DOI New ≥ Landed DOI Old + 4:** {num_skus}")
st.write("### SKUs where Landed DOI New ≥ Landed DOI Old + 4")
st.dataframe(sku_comparison_df)



# Exclude SKUs where Landed DOI Old is 0
filtered_df = filtered_df[filtered_df['Landed DOI OLD'] > 0]

# Apply the 0.8 factor to Landed DOI New
filtered_df['Landed DOI New Adjusted'] = filtered_df['Landed DOI New'] * 0.8

# Apply DOI filtering (optional, ensures values are within reasonable range)
filtered_df = filtered_df[(filtered_df['Landed DOI New Adjusted'] <= 100) & (filtered_df['Landed DOI OLD'] <= 100)]

# Calculate averages
avg_landed_doi_new2 = filtered_df['Landed DOI New Adjusted'].mean()
avg_landed_doi_old2 = filtered_df['Landed DOI OLD'].mean()

# Display results with 2 decimal places
st.write(f"**Average Landed DOI New (Adjusted):** {avg_landed_doi_new2:.2f}")
st.write(f"**Average Landed DOI Old:** {avg_landed_doi_old2:.2f}")

# Find SKUs where Adjusted Landed DOI New is at least Landed DOI Old + 4
sku_comparison_df2 = filtered_df[filtered_df['Landed DOI New Adjusted'] >= (filtered_df['Landed DOI OLD'] + 4)][['product_name', 'Landed DOI New Adjusted', 'Landed DOI OLD']]

# Count number of SKUs
num_skus2 = len(sku_comparison_df2)

# Display count
st.write(f"**Total Number of SKUs where Adjusted Landed DOI New ≥ Landed DOI Old + 4:** {num_skus2}")

# Display DataFrame
st.write("### SKUs where Adjusted Landed DOI New ≥ Landed DOI Old + 4")
st.dataframe(sku_comparison_df2)









# Product ID filter
st.markdown("----")

st.subheader("SKU Level View")
analisa_df["product_display"] = analisa_df["product_id"].astype(str) + " - " + analisa_df["product_name"]

# Create a dictionary to map the display name back to the Product ID
product_map = dict(zip(analisa_df["product_display"], analisa_df["product_id"]))

# Selectbox with formatted product ID and name
selected_product_display = st.selectbox("Select Product", list(product_map.keys()))

# Filter the dataframe using the actual Product ID
selected_product_id = product_map[selected_product_display]
filtered_df = analisa_df[analisa_df['product_id'] == selected_product_id]

#filtered_df['Landed DOI New'] = filtered_df['Landed DOI New']*0.8
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
        "Category": ["Landed DOI Old", "Landed DOI New"],
        "Value": [filtered_df['Landed DOI OLD'].mean(), filtered_df['Landed DOI New'].mean()]
    })

    fig_doi = px.bar(landed_doi_data, y="Value", x="Category", orientation='v',
                     title="Comparison of Landed DOI New vs Old", color="Category",
                     color_discrete_map={"Landed DOI New": "rgb(119, 221, 119)", "Landed DOI Old": "rgb(255, 153, 153)"})

    st.plotly_chart(fig_doi, use_container_width=True)

# RL Quantity Comparison
with col2:
    rl_qty_data = pd.DataFrame({
        "Category": ["RL Qty Actual", "RL Qty NEW after MIN QTY WH"],
        "Value": [filtered_df['RL Qty Actual'].mean(), filtered_df['RL Qty NEW after MIN QTY WH'].mean()]
    })

    fig_rl = px.bar(rl_qty_data, y="Value", x="Category", orientation='v',
                    title="Comparison of RL Qty", color="Category",
                    color_discrete_map={"RL Qty Actual": "rgb(255, 153, 153)", "RL Qty NEW after MIN QTY WH": "rgb(119, 221, 119)"})

    st.plotly_chart(fig_rl, use_container_width=True)


