import streamlit as st
import pandas as pd
import zipfile
import os
from datetime import datetime, timedelta

# === CONFIG ===
GTFS_STATIC_ZIP = "gtfs_rapid_bus_kl.zip"  # Place your GTFS zip here
EXTRACTED_DIR = "static_gtfs"

# === Extract GTFS Zip if not already extracted ===
if not os.path.exists(EXTRACTED_DIR):
    with zipfile.ZipFile(GTFS_STATIC_ZIP, 'r') as zip_ref:
        zip_ref.extractall(EXTRACTED_DIR)

# === Load GTFS Static Data ===
trips_df = pd.read_csv(os.path.join(EXTRACTED_DIR, "trips.txt"))
stop_times_df = pd.read_csv(os.path.join(EXTRACTED_DIR, "stop_times.txt"))
stops_df = pd.read_csv(os.path.join(EXTRACTED_DIR, "stops.txt"))
calendar_df = pd.read_csv(os.path.join(EXTRACTED_DIR, "calendar.txt"))
routes_df = pd.read_csv(os.path.join(EXTRACTED_DIR, "routes.txt"))

# === Merge to Get Friendly Stop Names ===
stop_names = stop_times_df.merge(stops_df, on="stop_id")[["stop_id", "stop_name"]].drop_duplicates()
stop_names = stop_names.sort_values("stop_name")
stop_options = stop_names.apply(lambda row: f"{row['stop_name']} ({row['stop_id']})", axis=1).tolist()

# === Streamlit UI ===
st.title("🚌 GTFS Static Schedule Viewer")
st.markdown("Select a stop to estimate the next bus based on static schedule data.")

selected_stop = st.selectbox(
    "🛑 Select a Stop",
    stop_options,
    index=0,
    placeholder="Type to search a bus stop..."
)

selected_stop_id = selected_stop.split("(")[-1].strip(")")

# === Get Current Time and Day of Week ===
now = datetime.now()
current_time_str = now.strftime("%H:%M:%S")
current_day = now.strftime("%A").lower()

# Debug: Show the current day and the actual calendar data
st.write(f"Current Day: {current_day}")
st.write(f"Calendar Data: {calendar_df.head()}")

# === Find Service IDs Running Today ===
valid_services = calendar_df[
    (calendar_df[current_day] == 1) &
    (calendar_df['start_date'] <= int(now.strftime("%Y%m%d"))) &
    (calendar_df['end_date'] >= int(now.strftime("%Y%m%d")))
]['service_id'].tolist()

# Debug print for valid services
st.write(f"Valid Services for Today ({current_day}): {valid_services}")

# === Ensure Stop ID Matches and Clean Up Stop Times Data ===
# Strip leading/trailing spaces in stop_id
stop_times_df['stop_id'] = stop_times_df['stop_id'].astype(str).str.strip()

# === Merge stop_times with trips to get service_id ===
merged_stop_times = stop_times_df.merge(trips_df[['trip_id', 'service_id', 'route_id']], on='trip_id', how='left')

# Debug: Check merged stop_times with service_id
st.write(f"Merged Stop Times with Service ID: {merged_stop_times.head()}")

# === Filter stop_times for selected stop and valid service ===
stop_times_filtered = merged_stop_times[
    (merged_stop_times['stop_id'] == selected_stop_id) &
    (merged_stop_times['service_id'].isin(valid_services))
]

# Debug: Check if stop_times_filtered is correct
st.write(f"Filtered Stop Times: {stop_times_filtered.head()}")

# === Merge with trips to filter valid service_ids ===
# Ensure service_id column is retained
merged = stop_times_filtered.merge(trips_df[['trip_id', 'service_id']], on='trip_id', how='left')

# Debug: Check merged data after adding service_id
st.write(f"Merged Data (After Filtering Service IDs): {merged.head()}")

# === Filter upcoming times ===
merged['arrival_time'] = pd.to_datetime(merged['arrival_time'], format='%H:%M:%S', errors='coerce').dt.time
now_time = pd.to_datetime(now.strftime('%H:%M:%S')).time()

# Debug: Check arrival times after conversion
st.write(f"Current Time: {now_time}")
st.write(f"Filtered Merged (After Arrival Time Comparison): {merged.head()}")

# Filter for upcoming buses only
merged = merged[merged['arrival_time'] > now_time]

# === Sort and Display Next Few Arrivals ===
merged = merged.sort_values('arrival_time')
next_buses = merged[['route_id', 'trip_id', 'arrival_time']].head(5)

# Debug: Check final buses
st.write(f"Next Buses (Final): {next_buses}")

if not next_buses.empty:
    st.success(f"✅ Upcoming buses for **{selected_stop}**:")
    st.dataframe(next_buses.rename(columns={"route_id": "Route", "trip_id": "Trip", "arrival_time": "Arrival Time"}))
else:
    st.info("🚫 No more scheduled buses for today at this stop.")
