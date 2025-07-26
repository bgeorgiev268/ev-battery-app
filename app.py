import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# -------------------
# Streamlit App Setup
# -------------------
st.title("EV Battery Complaint Dashboard")
st.caption("Powered by NHTSA API")

# Sidebar Inputs
manufacturer = st.selectbox("Select Manufacturer", ["Tesla", "Rivian", "Lucid"])
year = st.selectbox("Select Model Year", list(range(2020, 2026)))

# -------------------
# Fetch Complaints from NHTSA
# -------------------
@st.cache_data
def fetch_complaints(make, year):
    url = f"https://www.nhtsa.gov/webapi/api/Complaints/vehicle/modelyear/{year}/make/{make}/model/all?format=json"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("Results", [])

complaints = fetch_complaints(manufacturer, year)

# -------------------
# Filter for Battery-Related Complaints
# -------------------
battery_complaints = [c for c in complaints if "battery" in c["Summary"].lower()]
battery_df = pd.DataFrame(battery_complaints)

# -------------------
# Display Results
# -------------------
st.subheader(f"🔋 Battery Complaints for {manufacturer} ({year})")
st.write(f"Total Complaints Found: **{len(battery_complaints)}**")

if not battery_df.empty:
    # Format date and count by month
    battery_df["Date"] = pd.to_datetime(battery_df["DateReceived"])
    monthly = battery_df.groupby(battery_df["Date"].dt.to_period("M")).size()

    # Plot complaint trend
    fig, ax = plt.subplots()
    monthly.plot(kind="bar", ax=ax)
    ax.set_title("Battery Complaints Over Time")
    ax.set_ylabel("Number of Complaints")
    ax.set_xlabel("Month")
    st.pyplot(fig)

    # Show table
    st.dataframe(battery_df[["ODIN", "Summary", "DateReceived", "City", "State"]])
else:
    st.info("No battery complaints found for this make and year.")


