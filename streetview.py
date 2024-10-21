import math
import random
import os
from api import get_panorama_id, get_street_name, capture_street_view_image

class StreetView:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_points_in_radius(self, center_lat, center_lon, radius_km, num_points):
        points = []
        for _ in range(num_points):
            angle = math.radians(random.uniform(0, 360))
            distance = random.uniform(0, radius_km)
            
            lat_offset = distance / 111.32
            lon_offset = distance / (111.32 * math.cos(math.radians(center_lat)))
            
            new_lat = center_lat + (lat_offset * math.cos(angle))
            new_lon = center_lon + (lon_offset * math.sin(angle))
            
            points.append((new_lat, new_lon))
        
        return points

    def capture_images_in_radius(self, center_lat, center_lon, radius_km, num_points, output_dir):
        points = self.generate_points_in_radius(center_lat, center_lon, radius_km, num_points)
        metadata = []
        
        for i, (lat, lon) in enumerate(points):
            pano_id = get_panorama_id(lat, lon, self.api_key)
            if pano_id:
                street_name = get_street_name(lat, lon, self.api_key)
                for heading in range(0, 360, 90):
                    image_filename = f"street_view_{i}_{heading}.jpg"
                    output_path = os.path.join(output_dir, image_filename)
                    if capture_street_view_image(lat, lon, heading, output_path, self.api_key):
                        metadata.append({
                            "image_filename": image_filename,
                            "latitude": lat,
                            "longitude": lon,
                            "heading": heading,
                            "street_name": street_name,
                            "panorama_id": pano_id
                        })
        
        return metadata