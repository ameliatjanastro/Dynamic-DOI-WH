import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


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
            font-size: 10px !important;  /* Ensures default or larger font */
        }
        
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app title
st.markdown("<h1 style='color: rgb(0, 0, 128);'>Why use L2PO for DOI Policy?</h1>", unsafe_allow_html=True)
st.subheader("<h4 style='color: rgb(0, 0, 128);'>Overall View</h4>")
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
inb_df['OOS Date'] = inb_df['Date'] + pd.Timedelta(days=2)
inb_df['OOS Date'] = pd.to_datetime(inb_df['OOS Date']).dt.date # Convert to date only (removes time)


# Merge inbound data with total data on adjusted OOS dates
merged_df = pd.merge(total_df, inb_df[['Date', 'OOS Date', 'Actual', 'Max Projected']],
                     left_on='Date', right_on='OOS Date', how='left')

# Calculate projected OOS% based on inbound quantity ratio
merged_df['Projected % OOS Contribution'] = (merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])).round(2)
merged_df2 = merged_df[['Date_y', 'Actual', 'Max Projected', '% OOS Contribution', 'Projected % OOS Contribution']]
merged_df2.rename(columns={'Date_y': 'Date'}, inplace=True) 
merged_df2 = merged_df2.sort_values(by='Date', ascending=True)
col1, col2 = st.columns([1, 3])
with col2:
  st.dataframe(merged_df2, hide_index=True, use_container_width = True)
with col1:
    # Text area for notes
    st.markdown("""
  **Background:**  
  - Data is from cycle 3-6 Feb RL Upload -> Inbound 10-15 Feb.  
  - Assume 2 days buffer SO -> OOS reflected 2 days post Inbound.  
  - Accounts for OOS WH Fulfill x On Time.
  
  **Actual RL:** <span style='color: maroon; font-weight: 600; font-style: italic;'>974,365</span>  
  **Projected RL:** <span style='color: green; font-weight: 600; font-style: italic;'>1,214,641</span>  
  """, unsafe_allow_html=True)

analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = analisa_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
analisa_df['Landed DOI New'] = analisa_df['Landed DOI New'].fillna(0)
analisa_df['Landed DOI OLD'] = analisa_df['Landed DOI OLD'].fillna(0)
analisa_df[['Landed DOI New', 'Landed DOI OLD']] = analisa_df[['Landed DOI New', 'Landed DOI OLD']].apply(pd.to_numeric, errors='coerce')

analisa_df['RL Qty Actual'] = analisa_df['RL Qty Actual'].fillna(0)
analisa_df['RL Qty NEW after MIN QTY WH'] = analisa_df['RL Qty NEW after MIN QTY WH'].fillna(0)

# Plot actual vs projected inbound quantity

fig_inb = px.bar(inb_df, x='Date', y=['Actual', 'Max Projected'],
                 labels={'value': 'Inbound Quantity', 'variable': 'Type'},
                 title='Actual vs Projected Inbound Quantity',
                 barmode='group')

fig_inb.for_each_trace(lambda t: t.update(name="Actual" if t.name == "Actual" else "Project"))

fig_inb.update_layout(
    width=700,  # Reduce width
    height=400,  # Reduce height
    margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins
    legend=dict(
        font=dict(size=8)
    )  # Make legend text smaller
)

# Create the OOS percentage line chart
fig_oos = px.line(merged_df, x='OOS Date', y=['% OOS Contribution', 'Projected % OOS Contribution'],
                  labels={'value': 'OOS %', 'variable': 'Type'},
                  title='Actual vs Projected Out-of-Stock Percentage Trend')

fig_oos.for_each_trace(lambda t: t.update(name="Actual" if t.name == "% OOS Contribution" else "Project"))

fig_oos.update_layout(
    width=700,  # Reduce width
    height=400,  # Reduce height
    margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins
    legend=dict(
        font=dict(size=8)
    )  # Make legend text smaller
)

# Selectbox for choosing which chart to display
with st.expander("View Inbound Qty and OOS Graphs"):
    
    chart_option = st.selectbox("Select a graph to display:", ["Inbound Quantity Comparison", "Out-of-Stock % Comparison"])
    
    # Display the selected chart
    if chart_option == "Inbound Quantity Comparison":
        st.plotly_chart(fig_inb)
        # Sum RL and Inbound quantities
        rl_actual = analisa_df['RL Qty Actual'].sum()
        rl_new = analisa_df['RL Qty NEW after MIN QTY WH'].sum()
        inb_actual = inb_df['Actual'].sum()
        inb_max_projected = inb_df['Max Projected'].sum()
        
        # Create a DataFrame for stacked bars
        conversion_data = pd.DataFrame({
            'Category': ['Actual', 'Projected'],
            'RL Qty': [rl_actual, rl_new],  # RL values (bottom of the stack)
            'Inbound Qty': [inb_actual, inb_max_projected]  # Inbound values (stacked on top)
        })
        
        # Melt DataFrame into long format for Plotly
        conversion_data = conversion_data.melt(id_vars=['Category'], var_name='Type', value_name='Quantity')
        
        # Define custom colors: lighter gray for RL, pastel green for Inbound
        color_map = {'RL Qty': '#d3d3d3', 'Inbound Qty': '#77dd77'}  # Light gray & pastel green
        
        # Create a stacked bar chart using Plotly
        fig = px.bar(
            conversion_data,
            x='Quantity',
            y='Category',
            color='Type',
            orientation='h',
            title="RL to Inbound Qty Conversion",
            text='Quantity',
            color_discrete_map=color_map
        )
        
        # Ensure bars are stacked properly
        fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
        fig.update_layout(
            xaxis_title="Total Quantity",
            yaxis_title="",
            showlegend=False,
            barmode='relative',
            margin=dict(l=20, r=20, t=20, b=20), # This ensures stacking instead of side-by-side bars
            height=150  # Reduce chart height
        )
        
        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=False)  # Reduce overall size
    
    
    else:
        st.plotly_chart(fig_oos)
    
st.markdown("----")

st.subheader("<h4 style='color: rgb(0, 0, 128);'>Deep Dive into RL Engine</h4>")


st.markdown("First we excluded some SKUs, Focus on SKUs with Landed DOI Increase/Decrease :):")
excluded_df = analisa_df[
    analisa_df['Verdict'].isin([
        'Excluded, out of scope since current doi > 100', 'Excluded, same order qty or gaorder','Landed DOI Sama'
    ])
][['product_id', 'product_name','l1_category_name', 'RL Qty Actual', 'RL Qty NEW after MIN QTY WH','Why Increase/Decrease?','Verdict']]

grouped_exclude = excluded_df.groupby('Verdict', as_index=False).agg(
    Product_Count=('product_id', 'nunique')
)

grouped_exclude.rename(columns={
    'Product_Count': 'Count SKU'
}, inplace=True)

col1, col2 = st.columns([2.5, 2])
with col1:
    st.dataframe(grouped_exclude, hide_index=True, use_container_width= True)

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
    'Product_Count': 'Count SKU',
    'Mode_Why_Increase_Decrease': 'Mode Reason'
}, inplace=True)

grouped_df1 = grouped_df1.sort_values(by='Count SKU', ascending=False)


# Calculate summary statistics
total_products = filtered_df1['product_id'].nunique()  # Count unique products
total_rl_qty_new = filtered_df1['RL Qty NEW after MIN QTY WH'].sum().astype(int)  # Sum of RL Qty NEW
total_rl_qty_old = filtered_df2['RL Qty Actual'].sum().astype(int)
total_productsold = filtered_df2['product_id'].nunique()
landed_doi_yg_gaorder = filtered_df2['Landed DOI New'].mean().astype(float)

# Display the table without an index

st.markdown("Below are the total no. of SKUs that we **did not** order but **would order** with new doi policy:")
col1, col2 = st.columns([2.5, 2])
with col1:
  st.dataframe(grouped_df1, hide_index=True, use_container_width= True)
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

st.markdown("----")

st.subheader("<h6>Landed DOI Comparison -  only for KOS</h6>")

col1, col2 = st.columns(2)

# Multiselect filters
with col1:
    filtered_df = analisa_df.copy()
    
    allowed_location = filtered_df[filtered_df ['location_id'] == 40]['location_id'].unique()
    selected_location = st.selectbox("Select Location:", allowed_location)

# Get unique categories and add "All" option
filtered_df = filtered_df[filtered_df['Landed DOI OLD'].notna()]
# Exclude rows where l1_category_name contains "OFF"
filtered_df = filtered_df[~filtered_df['l1_category_name'].str.contains("Olahraga|OFF|Private", na=False, case=False)]
available_categories = ["All"] + list (filtered_df[(filtered_df['location_id'] == 40)]['l1_category_name'].unique())

with col2:
    selected_category = st.selectbox("Select L1 Category:", available_categories)

# Apply category filtering (skip if "All" is selected)
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['l1_category_name'] == selected_category]

filtered_df = filtered_df[(filtered_df['Landed DOI OLD'] != 0) & (~filtered_df['product_id'].isin(excluded_df['product_id']))]

filtered_df['Landed DOI New Adjusted'] = filtered_df['Landed DOI New'] * 0.8
high_diff_mask = (filtered_df['Landed DOI New'] - filtered_df['Landed DOI OLD']) > 6

# Apply an additional 25% reduction for those rows
filtered_df.loc[high_diff_mask, 'Landed DOI New Adjusted'] *= 0.9  # Reduce by 10%

# Apply DOI filtering (optional, ensures values are within reasonable range)
filtered_df = filtered_df[(filtered_df['Landed DOI New Adjusted'] <= 100)]

# Calculate averages
avg_landed_doi_new2 = filtered_df['Landed DOI New Adjusted'].mean()

# Calculate averages
avg_landed_doi_new = filtered_df['Landed DOI New'].mean()
avg_landed_doi_old = filtered_df['Landed DOI OLD'].mean()

# Display results with 2 decimal places
st.write(f"**Average Landed DOI New:** {avg_landed_doi_new2:.2f}")
st.write(f"**Average Landed DOI Old:** {avg_landed_doi_old:.2f}")

# Find SKUs where Landed DOI New is at least Landed DOI Old + 4
sku_comparison_df2 = filtered_df[filtered_df['Landed DOI New Adjusted'] >= (filtered_df['Landed DOI OLD'] + 4)][['product_id','product_name', 'Landed DOI New Adjusted', 'Landed DOI OLD']]
# Convert Landed DOI New Adjusted to integer (round down)
sku_comparison_df2['Landed DOI New Adjusted'] = np.floor(sku_comparison_df2['Landed DOI New Adjusted']).astype(int)
# Sort by largest Landed DOI New Adjusted
sku_comparison_df2['product_id'] = sku_comparison_df2['product_id'].astype(int)
sku_comparison_df2 = sku_comparison_df2.sort_values(by='product_id', ascending=True)
# Count number of SKUs
num_skus2 = len(sku_comparison_df2)

# Display count
st.write(f"**Total Number of SKUs where Landed DOI New ≥ Landed DOI Old + 4:** {num_skus2}")

# Display DataFrame
sku_comparison_df2 = sku_comparison_df2.rename(columns={
    'product_name': 'Product Name',
    'Landed DOI New Adjusted': 'Landed DOI New',
    'Landed DOI OLD': 'Landed DOI Old'
})

sku_comparison_df2['Landed DOI Old'] = sku_comparison_df2['Landed DOI Old'].astype(int)
sku_comparison_df2['Landed DOI New'] = sku_comparison_df2['Landed DOI New'].astype(int)


# Function to apply conditional styling
def highlight_large_doi_diff(row):
    """Highlight rows in pastel yellow if Landed DOI New - Landed DOI Old > 15."""
    color = 'background-color: #FFF9C4' if (row['Landed DOI New'] - row['Landed DOI Old']) > 15 else ''
    return [color] * len(row)

# Apply styling
styled_df = sku_comparison_df2.style.apply(highlight_large_doi_diff, axis=1)

# Display in Streamlit
st.dataframe(styled_df)

# Product ID filter
st.markdown("----")

st.subheader("<h4 style='color: rgb(0, 0, 128);'>SKU Level View</h4>")
# Create a separate DataFrame for SKU Level View
filtered_sku_df = analisa_df.copy()

# Keep only location 40
filtered_sku_df = filtered_sku_df[filtered_sku_df['location_id'] == 40]

# Exclude rows where Landed DOI OLD is NaN
filtered_sku_df = filtered_sku_df[filtered_sku_df['Landed DOI OLD'].notna()]

# Exclude categories containing "Olahraga", "OFF", or "Private"
filtered_sku_df = filtered_sku_df[~filtered_sku_df['l1_category_name'].str.contains("Olahraga|OFF|Private", na=False, case=False)]

# Apply Landed DOI Adjustments
filtered_sku_df['Landed DOI New Adjusted'] = filtered_sku_df['Landed DOI New'] * 0.8

# Apply additional 10% reduction if Landed DOI New - Landed DOI OLD > 6
high_diff_mask2 = (filtered_sku_df['Landed DOI New'] - filtered_sku_df['Landed DOI OLD']) > 6
filtered_sku_df.loc[high_diff_mask2, 'Landed DOI New Adjusted'] *= 0.9  # Reduce by 10%






filtered_sku_df['product_id'] = filtered_sku_df['product_id'].astype(int)
filtered_sku_df["product_display"] =  filtered_sku_df["product_id"].astype(str) + " - " +  filtered_sku_df["product_name"]

# Create a dictionary to map the display name back to the Product ID
product_map = dict(zip( filtered_sku_df["product_display"],  filtered_sku_df["product_id"]))

# Selectbox with formatted product ID and name
selected_product_display = st.selectbox("Select Product", list(product_map.keys()))

# Filter the dataframe using the actual Product ID
selected_product_id = product_map[selected_product_display]
filtered_df2 =  filtered_sku_df[ filtered_sku_df['product_id'] == selected_product_id]

filtered_df2['Landed DOI New Adjusted'] = filtered_sku_df['Landed DOI New Adjusted'].fillna(0).astype(int)
filtered_df2['Landed DOI OLD'] = filtered_sku_df['Landed DOI OLD'].fillna(0)
filtered_df2['RL Qty NEW after MIN QTY WH'] = filtered_sku_df['RL Qty NEW after MIN QTY WH'].fillna(0)
filtered_df2[['Landed DOI New Adjusted', 'Landed DOI OLD']] = filtered_sku_df[['Landed DOI New Adjusted', 'Landed DOI OLD']].astype(float)
filtered_df2[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']] = filtered_sku_df[['RL Qty Actual', 'RL Qty NEW after MIN QTY WH']].astype(float)

# Landed DOI Comparison
col1, col2 = st.columns(2)

# Landed DOI Comparison
with col1:
    landed_doi_data = pd.DataFrame({
        "Category": ["Old", "New"],
        "Value": [filtered_df2['Landed DOI OLD'].mean(), filtered_df2['Landed DOI New Adjusted'].mean()]
    })

    fig_doi = px.bar(landed_doi_data, y="Value", x="Category", orientation='v',
                     title="Comparison of Landed DOI New vs Old", color="Category",
                     color_discrete_map={"New": "rgb(119, 221, 119)", "Old": "rgb(255, 153, 153)"})
    
    fig_doi.update_layout(
        width=320,  # Increase width
        height=400,  # Increase height
        margin=dict(l=10, r=10, t=50, b=30),  # Adjust margins
        legend=dict(font=dict(size=8))  # Slightly increase legend text size
    )

    st.plotly_chart(fig_doi, use_container_width=False)

# RL Quantity Comparison
with col2:
    rl_qty_data = pd.DataFrame({
        "Category": ["Actual", "Project"],
        "Value": [filtered_df2['RL Qty Actual'].mean(), filtered_df2['RL Qty NEW after MIN QTY WH'].mean()]
    })

    fig_rl = px.bar(rl_qty_data, y="Value", x="Category", orientation='v',
                    title="Comparison of RL Qty", color="Category",
                    color_discrete_map={"Actual": "rgb(255, 153, 153)", "Project": "rgb(119, 221, 119)"})

    fig_rl.update_layout(
        width=320,  # Increase width
        height=400,  # Increase height
        margin=dict(l=10, r=19, t=50, b=30),  # Adjust margins
        legend=dict(font=dict(size=8))  # Slightly increase legend text size
    )

    st.plotly_chart(fig_rl, use_container_width=False)


