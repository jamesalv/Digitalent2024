import os
import json
import requests
import torch
from PIL import Image
from dotenv import load_dotenv
from ultralytics import YOLO
import streamlit as st
import folium
from streamlit_folium import st_folium
import cv2

# Load environment variables
load_dotenv()

# YOLO Model
model = YOLO("models/best_detect.pt")

# Flask API base URL (change if your Flask server runs on another IP/port)
FLASK_API_URL = "http://127.0.0.1:5000"

def get_street_name(lat, lon):
    """Fetch the street name from the Flask API."""
    url = f"{FLASK_API_URL}/get_street_name"
    response = requests.get(url, params={"lat": lat, "lon": lon})
    if response.status_code == 200:
        return response.json().get("street_name", "Unknown Street")
    return "Unknown Street"

def capture_image(lat, lon, heading, output_path):
    """Request the Flask API to capture a Street View image."""
    url = f"{FLASK_API_URL}/capture_image"
    payload = {
        "lat": lat,
        "lon": lon,
        "heading": heading,
        "output_path": output_path
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

def detect_potholes(image_path, detection_dir, conf):
    """Detect potholes in the given image using the YOLO model."""
    image_filename = os.path.basename(image_path)
    results = model.predict(source=image_path, conf=conf)[0]

    potholes = []
    if len(results.boxes) > 0:
        # Get the annotated image in BGR format
        annotated_img = results.plot()
        
        # Convert BGR to RGB
        annotated_img_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        
        detection_path = os.path.join(detection_dir, image_filename)
        Image.fromarray(annotated_img_rgb).save(detection_path)

        for box in results.boxes:
            if results.names[int(box.cls[0])] == 'road-pothole':
                detection = {
                    'bbox': box.xyxy[0].tolist(),
                    'confidence': float(box.conf[0]),
                    'class': 'road-pothole'
                }
                potholes.append(detection)

    return potholes

def capture_images_and_detect_potholes(center_lat, center_lon, radius_km, num_points, conf, output_dir):
    """Capture Street View images and detect potholes."""
    os.makedirs(output_dir, exist_ok=True)
    detection_dir = os.path.join(output_dir, "street_view_detection")
    os.makedirs(detection_dir, exist_ok=True)

    pothole_detections = []

    # Loop over specified points and capture images
    for i in range(num_points):
        heading = i * (360 // num_points)  # Distribute headings evenly
        output_path = os.path.join(output_dir, f"street_view_{i}.jpg")

        # Capture image through Flask API
        if capture_image(center_lat, center_lon, heading, output_path):
            potholes = detect_potholes(output_path, detection_dir, conf)
            if potholes:
                street_name = get_street_name(center_lat, center_lon)
                detection_data = {
                    "latitude": center_lat,
                    "longitude": center_lon,
                    "street_name": street_name,
                    "potholes": potholes,
                    "annotated_image": os.path.join("street_view_images", "street_view_detection", f"street_view_{i}.jpg")
                }
                pothole_detections.append(detection_data)

    # Save metadata to JSON
    metadata_file = os.path.join(output_dir, "pothole_detections.json")
    with open(metadata_file, "w") as f:
        json.dump(pothole_detections, f, indent=2)

    return pothole_detections

# Initialize session state for coordinates if not already set
if 'lat' not in st.session_state:
    st.session_state.lat = -6.9729215
if 'lon' not in st.session_state:
    st.session_state.lon = 110.3904476

st.title("Pothole Detection from Google Street View")

# Create a map centered at the current coordinates
m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15)

# Add a marker at the current position
folium.Marker(
    [st.session_state.lat, st.session_state.lon],
    popup=f"Selected Location<br>Lat: {st.session_state.lat:.7f}<br>Lon: {st.session_state.lon:.7f}",
    icon=folium.Icon(color="red", icon="info-sign"),
).add_to(m)

# Display the map and capture click events
map_data = st_folium(m, height=300, width=700)

# Update coordinates when map is clicked
if map_data['last_clicked']:
    st.session_state.lat = map_data['last_clicked']['lat']
    st.session_state.lon = map_data['last_clicked']['lng']
    st.rerun()

# Form for user input with values from session state
with st.form("location_form"):
    st.write("Select a point on the map or enter coordinates manually:")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input(
            "Latitude",
            value=st.session_state.lat,
            format="%.7f",
            step=0.0000001
        )
    with col2:
        lon = st.number_input(
            "Longitude",
            value=st.session_state.lon,
            format="%.7f",
            step=0.0000001
        )
    
    col3, col4 = st.columns(2)
    with col3:
        radius_km = st.number_input(
            "Radius (in km)",
            value=0.5,
            min_value=0.1,
            format="%.3f",
            step=0.001
        )
    with col4:
        num_points = st.number_input(
            "Number of Points",
            value=5,
            min_value=1,
            max_value=10
        )
    # Add slider for confidence threshold
    conf = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    
    submitted = st.form_submit_button("Detect Potholes")

if submitted:
    with st.spinner("Detecting potholes..."):
        output_dir = "street_view_images"
        detections = capture_images_and_detect_potholes(lat, lon, radius_km, num_points, conf, output_dir)

    # Display results (unchanged)
    if detections:
        st.success(f"Detected potholes in {len(detections)} images!")
        for detection in detections:
            st.write(f"Location: {detection['latitude']:.7f}, {detection['longitude']:.7f}")
            st.write(f"Street: {detection['street_name']}")
            st.image(detection['annotated_image'], caption="Annotated Image")
    else:
        st.warning("No potholes detected.")