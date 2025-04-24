import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
import time
import pandas as pd

# GTFS URL
GTFS_REALTIME_URL = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl"

# Fetch live GTFS data
def get_realtime_data():
    try:
        response = requests.get(GTFS_REALTIME_URL)

        if not response.content:
            st.error("⚠️ The API response is empty. Please try again later.")
            return None

        if response.status_code != 200:
            if response.status_code == 429:
                st.warning("⚠️ You're refreshing too quickly. Please wait a moment before trying again.")
            else:
                st.error("⚠️ API request failed. Status code: " + str(response.status_code))
            return None

        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            feed.ParseFromString(response.content)
            return feed
        except Exception as parse_error:
            st.error("⚠️ Failed to parse GTFS data. The data might be corrupted or not in the expected format.")
            st.error(f"Error Details: {str(parse_error)}")
            return None

    except requests.exceptions.RequestException as request_error:
        st.error("⚠️ There was an issue with the API request. Please check your internet connection or try again later.")
        st.error(f"Error Details: {str(request_error)}")
        return None

# Set default session state
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# UI: Title
st.title("🚍 Prasarana Real-Time Bus Viewer")

# Show loading spinner while data is being fetched
with st.spinner("Fetching vehicle data..."):
    feed = get_realtime_data()

# Extract vehicle data, trip updates, and service alerts
vehicle_ids = []
vehicles_data = []

if feed:
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            v_id = getattr(vehicle.vehicle, "id", None)
            if not v_id:
                v_id = getattr(vehicle.vehicle, "license_plate", "UNKNOWN")

            vehicle_data = {
                "Vehicle ID": v_id,
                "Timestamp": datetime.fromtimestamp(vehicle.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "Latitude": vehicle.position.latitude,
                "Longitude": vehicle.position.longitude,
                "License Plate": getattr(vehicle.vehicle, "license_plate", "N/A"),
            }

            # Check for trip_update and service_alert data
            trip_update = None
            service_alert = None

            if entity.HasField("trip_update"):
                trip_update = entity.trip_update
            if entity.HasField("alert"):
                service_alert = entity.alert

            # Add trip_update and service_alert data to the vehicle data
            vehicle_data["Trip Update"] = trip_update if trip_update else "No data"
            vehicle_data["Service Alert"] = service_alert if service_alert else "No data"

            vehicles_data.append(vehicle_data)

        elif entity.HasField("trip_update"):
            # Trip update data (e.g., delays, on-time status)
            trip_update = entity.trip_update
            trip_id = trip_update.trip.trip_id
            status = "On-time" if not trip_update.delay else f"Delayed by {trip_update.delay} seconds"

            vehicles_data.append({
                "Trip ID": trip_id,
                "Status": status,
                "Timestamp": datetime.fromtimestamp(trip_update.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            })

        elif entity.HasField("alert"):
            # Service alert data
            alert = entity.alert
            alert_id = alert.id
            alert_text = alert.header_text.translation[0].text if alert.header_text else "No details available"

            vehicles_data.append({
                "Alert ID": alert_id,
                "Alert": alert_text,
                "Timestamp": datetime.fromtimestamp(alert.timestamp).strftime("%Y-%m-%d %H:%M:%S") if alert.timestamp else "Unknown",
            })

# Populate dynamic dropdown
vehicle_id_options = sorted(set([v["Vehicle ID"] for v in vehicles_data]))
filter_options = ["Show All"] + vehicle_id_options

with st.container():
    selected_id = st.selectbox(
        "Filter by Vehicle ID",
        filter_options,
        key="vehicle_filter",
        label_visibility="visible",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔁 Refresh"):
            st.session_state.last_refresh = time.time()
            st.rerun()
    with col2:
        elapsed = int(time.time() - st.session_state.last_refresh)
        st.markdown(f"**⏱️ Last manual refresh: {elapsed} sec ago**")

# Filter based on selected vehicle ID
if selected_id != "Show All":
    vehicles_data = [v for v in vehicles_data if v["Vehicle ID"] == selected_id]

# Pagination and display
PAGE_SIZE = 10

if vehicles_data:
    vehicles_df = pd.DataFrame(vehicles_data)

    total_rows = len(vehicles_df)
    num_pages = (total_rows // PAGE_SIZE) + (1 if total_rows % PAGE_SIZE != 0 else 0)

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    current_page = st.session_state.current_page
    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_data = vehicles_df.iloc[start_idx:end_idx]

    st.dataframe(page_data)

    st.markdown("---")
    page_buttons = st.columns(min(num_pages, 5))

    for i, col in enumerate(page_buttons, 1):
        if i <= num_pages:
            if col.button(str(i), key=f"page_{i}", help=f"Go to page {i}"):
                st.session_state.current_page = i
                st.rerun()
else:
    st.info("No data available for the selected vehicle.")

# Improved Feedback System
def collect_feedback():
    st.subheader("💬 We Value Your Feedback")
    name = st.text_input("Your Name (optional)")
    feedback = st.text_area("Share your thoughts or suggestions:")

    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

    if st.button("Submit Feedback", key="submit_feedback") and not st.session_state.feedback_submitted:
        if feedback.strip():
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open("feedback.txt", "a") as f:
                f.write(f"{timestamp} | Name: {name or 'Anonymous'}\n{feedback}\n\n")
            st.success("🎉 Thank you for your feedback!")
            st.session_state.feedback_submitted = True
        else:
            st.warning("✏️ Please type your feedback before submitting.")

collect_feedback()
