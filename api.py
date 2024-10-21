import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import io

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_STREET_VIEW_API_KEY")

API_ENDPOINT = "https://maps.googleapis.com/maps/api/streetview"
GEOCODING_API_ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"

app = Flask(__name__)

def get_street_name(lat, lon, api_key):
    params = {"latlng": f"{lat},{lon}", "key": api_key}
    response = requests.get(GEOCODING_API_ENDPOINT, params=params)
    data = response.json()

    if data["status"] == "OK":
        for result in data["results"]:
            for component in result["address_components"]:
                if "route" in component["types"]:
                    return component["long_name"]
    return "Unknown Street"

def get_panorama_id(lat, lon, api_key):
    metadata_url = f"{API_ENDPOINT}/metadata?location={lat},{lon}&key={api_key}"
    response = requests.get(metadata_url)
    data = response.json()
    return data.get("pano_id")

def capture_street_view_image(lat, lon, heading, output_path, api_key):
    params = {
        "size": "640x640",
        "location": f"{lat},{lon}",
        "heading": heading,
        "fov": 90,
        "pitch": -30,
        "key": api_key
    }
    response = requests.get(API_ENDPOINT, params=params)

    if response.status_code == 200:
        # Convert image to RGB using PIL
        image_bytes = io.BytesIO(response.content)
        image = Image.open(image_bytes)
        
        # Convert to RGB if image is not already in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save the RGB image
        image.save(output_path, format='JPEG', quality=95)
        return {"message": f"Image saved: {output_path}"}
    else:
        return {"error": f"Failed to capture image at {lat}, {lon}, heading {heading}"}

@app.route("/get_street_name", methods=["GET"])
def api_get_street_name():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    street_name = get_street_name(lat, lon, API_KEY)
    return jsonify({"street_name": street_name})

@app.route("/get_panorama_id", methods=["GET"])
def api_get_panorama_id():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    pano_id = get_panorama_id(lat, lon, API_KEY)
    return jsonify({"pano_id": pano_id})

@app.route("/capture_image", methods=["POST"])
def api_capture_image():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    heading = data.get("heading", 0)
    output_path = data.get("output_path", "street_view_image.jpg")

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    result = capture_street_view_image(lat, lon, heading, output_path, API_KEY)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)