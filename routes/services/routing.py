import requests
from django.conf import settings
from routes.services.geocoding import GeocodingService
from routes.utils.polyline import decode_polyline


class RoutingService:

    BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

    def __init__(self):
        self.geocoder = GeocodingService()

    def get_route(self, start_city, start_state, end_city, end_state):
        start_lat, start_lng = self.geocoder.get_coordinates(start_city, start_state)
        end_lat, end_lng = self.geocoder.get_coordinates(end_city, end_state)

        headers = {
            "Authorization": settings.ORS_API_KEY,
            "Content-Type": "application/json",
        }

        body = {
            "coordinates": [
                [start_lng, start_lat],
                [end_lng, end_lat],
            ]
        }

        response = requests.post(self.BASE_URL, json=body, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        route = data["routes"][0]
        decoded_geometry = decode_polyline(route["geometry"])
        summary = route["summary"]
        
        

        return {
            "polyline": decoded_geometry, 
            "distance_miles": summary["distance"] / 1609.34,
            "duration_minutes": summary["duration"] / 60,
        }
