GTFS Transit Viewer: Static & Realtime Dashboard (Streamlit App)

---

```markdown
# 🚍 GTFS Transit Viewer: Static & Realtime Dashboard

A lightweight Streamlit web app to visualize **GTFS (General Transit Feed Specification)** data — both **static** and **realtime** — for RapidKL buses. This project serves as a demonstration and learning tool for transit data integration and visualization.

---

## 📊 Features

### ✅ GTFS Static Viewer
- Displays scheduled bus arrival times based on GTFS `stop_times.txt`
- Allows filtering by:
  - **Stop ID**
  - **Stop Name**
  - **Stop Description**
- Shows only upcoming scheduled buses based on the current time and calendar rules

### 📡 GTFS Realtime Dashboard *(Optional Integration)*
- Displays live bus data from a GTFS-RT (Realtime) feed
- Visualizes real-time vehicle positions and ETAs
- Integrates GTFS-RT feed parsing using protobuf or JSON endpoints

---

## 🧪 Use Case
This project was created as a **proof-of-concept (POC)** to:
- Understand the structure and usage of GTFS data (static + realtime)
- Build a simple dashboard for internal testing and demonstrations
- Explore real-time tracking and prediction of public transit vehicles

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** — for interactive UI
- **Pandas** — for data manipulation
- **GTFS Static Feed** — CSV files (`trips.txt`, `stop_times.txt`, etc.)
- **GTFS-RT Feed** — parsed from JSON or protobuf
- **GitHub** — for version control

---

## ▶️ How to Run

1. Clone this repo:
   ```bash
   git clone https://github.com/skhhks3953/gtfs-streamlit-viewer.git
   cd gtfs-streamlit-viewer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run main.py
   ```

## 🧠 Future Enhancements
- Live vehicle map view using `folium` or `pydeck`
- Historical performance analysis
- Schedule adherence metrics
- User-based location tracking

---

## 📁 Sample Folder Structure

```
gtfs-streamlit-viewer/
│
├── static_gtfs/                # Extracted GTFS static data
├── main.py                     # Streamlit app entry point
├── GTFS_static.py              # Static viewer logic
├── GTFS_realtime.py            # Realtime feed handler (optional)
├── requirements.txt            # Dependencies
└── README.md                   # Project readme
```

---

## 👤 Author

Created by [@skhhks3953](https://github.com/skhhks3953)

---

## 📎 License

This project is intended for learning, POCs, and portfolio use. Attribution appreciated if reused.
```
