import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load data

df = pd.read_csv("Dynamic DOI WH Analisis - SUMMARY.csv")

# Display raw data in Streamlit
st.title("New vs Old RL Quantity & OOS Performance Analysis")
st.write("### Raw Data Preview")
st.dataframe(df.head())

# Ensure necessary columns exist
required_cols = ["cycle", "L1 Category", "OLD", "NEW", "#Hub OOS karena WH", "# New Hub OOS"]
if not all(col in df.columns for col in required_cols):
    st.error("Missing required columns in the dataset.")
    st.stop()

# Sidebar filter for cycle
#selected_cycle = st.sidebar.selectbox("Select Cycle", df["cycle"].unique())
#df = df[df["cycle"] == selected_cycle]

# Compute RL Change & OOS Impact
df["RL Qty Change %"] = ((df["NEW"] - df["OLD"]) / df["OLD"]) * 100
df["OOS Impact"] = df["#Hub OOS karena WH"] - df["# New Hub OOS"]  # Change in OOS hubs

# Group by L1 Category
category_summary = df.groupby("L1 Category").agg({
    "OLD": "sum",
    "NEW": "sum",
    "#Hub OOS karena WH": "sum",
    "# New Hub OOS": "sum"
}).reset_index()

# Calculate improvement percentage
category_summary["RL Qty Change %"] = ((category_summary["NEW"] - category_summary["OLD"]) / category_summary["OLD"]) * 100
category_summary["OOS Improvement"] = category_summary["#Hub OOS karena WH"] - category_summary["# New Hub OOS"]

# Plot RL Change by L1 Category per Cycle
fig1 = px.bar(category_summary, x="L1 Category", y=["OLD", "NEW"],
              color="cycle", barmode="group", title="Old vs New RL Quantity by L1 Category per Cycle")
st.plotly_chart(fig1)

# Plot OOS impact by L1 Category per Cycle
fig2 = px.bar(category_summary, x="L1 Category", y="OOS Improvement", color="cycle",
              title="Improvement in OOS # by L1 Category per Cycle")
st.plotly_chart(fig2)

# Show RL % Change in a Line Chart per Cycle
fig3 = px.line(category_summary, x="L1 Category", y="RL Qty Change %", color="cycle", markers=True,
               title="Percentage Change in RL Quantity by L1 Category per Cycle")
st.plotly_chart(fig3)

st.write("### Key Insights")
st.write("- Positive RL % Change means increased RL quantity.")
st.write("- A decrease in OOS # suggests improved stock availability.")

