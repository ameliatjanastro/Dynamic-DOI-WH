import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Streamlit app title
st.title("Inbound vs OOS Analysis")

# Upload CSV files
#inb_file = st.file_uploader("Upload Inbound CSV", type=["csv"])
#total_file = st.file_uploader("Upload Total CSV", type=["csv"])

if inb_file and total_file:
    # Load the data
    inb_df = pd.read_csv("inb.csv")
    total_df = pd.read_csv("total.csv")

    # Ensure date columns are in datetime format
    inb_df['Date'] = pd.to_datetime(inb_df['Date'])
    total_df['Date'] = pd.to_datetime(total_df['Date'])

    # Adjust inbound dates to align with OOS dates (OOS dates = Inb dates +2)
    inb_df['OOS_Date'] = inb_df['Date'] + pd.Timedelta(days=2)

    # Merge inbound data with total data on adjusted OOS dates
    merged_df = pd.merge(total_df, inb_df[['OOS_Date', 'Actual', 'Max Projected']],
                         left_on='Date', right_on='OOS_Date', how='left')

    # Calculate projected OOS% based on inbound quantity ratio
    merged_df['Projected % OOS Contribution'] = merged_df['% OOS Contribution'] * (merged_df['Actual'] / merged_df['Max Projected'])

    # Display data
    st.subheader("Merged Data Preview")
    st.write(merged_df.head())

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

    # Bar plot for inbound quantities with OOS overlay
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

    st.pyplot(fig)
