<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pothole Detection System</title>
</head>
<body>
    <h1>Pothole Detection System using Google Street View and YOLO</h1>

    <h2>Introduction</h2>
    <p>This application captures images from Google Street View based on user-specified coordinates and performs pothole detection using a YOLO model. The results are displayed along with annotated images showing the detected potholes.</p>

    <h2>Prerequisites</h2>
    <ul>
        <li>Python 3.x</li>
        <li>PIP (Python package installer)</li>
        <li>Google API Key with access to Street View and Geocoding APIs</li>
    </ul>

    <h2>Installation</h2>
    <ol>
        <li>Clone the repository or download the code:</li>
        <pre><code>git clone https://github.com/your-repo/pothole-detection.git</code></pre>

        <li>Navigate to the project directory:</li>
        <pre><code>cd pothole-detection</code></pre>

        <li>Install required dependencies:</li>
        <pre><code>pip install -r requirements.txt</code></pre>

        <li>Create a <code>.env</code> file and add your Google API key:</li>
        <pre><code>GOOGLE_STREET_VIEW_API_KEY=your_api_key_here</code></pre>
    </ol>

    <h2>Usage</h2>
    <ol>
        <li>Run the Flask server for the API:</li>
        <pre><code>python api.py</code></pre>

        <li>Launch the Streamlit interface:</li>
        <pre><code>streamlit run main.py</code></pre>

        <li>In the Streamlit interface, select a point on the map or enter coordinates manually. Specify the radius and number of points, then click "Detect Potholes".</li>
    </ol>

    <h2>Project Structure</h2>
    <ul>
        <li><code>api.py</code>: Flask server for capturing street view images and metadata.</li>
        <li><code>main.py</code>: Streamlit app for user interaction and displaying results.</li>
        <li><code>requirements.txt</code>: List of dependencies.</li>
    </ul>

    <h2>Example Output</h2>
    <p>Annotated images with potholes marked, along with metadata about the detection.</p>

    <h2>License</h2>
    <p>This project is licensed under the MIT License.</p>
</body>
</html>
