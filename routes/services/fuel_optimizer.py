from decimal import Decimal
from django.db.models import F
from routes.models import FuelStation
from geopy.distance import geodesic


class FuelOptimizer:

    MAX_RANGE = 500
    MPG = 10

    def optimize(self, route):
        route_points = route["polyline"]
        total_distance = route["distance_miles"]

        stations = self._stations_near_route(route_points)

        fuel_stops = self._select_stops(route_points, stations)

        total_cost = self._calculate_cost(total_distance, fuel_stops)

        return {
            "route": route["polyline"],
            "distance_miles": total_distance,
            "fuel_stops": fuel_stops,
            "total_fuel_cost": round(total_cost, 2),
        }

    def _stations_near_route(self, route_points):
        """
        Fetch stations within bounding box of route.
        Avoid full table scan.
        """

        lats = [pt[1] for pt in route_points]
        lngs = [pt[0] for pt in route_points]

        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)

        return FuelStation.objects.filter(
            latitude__range=(min_lat, max_lat),
            longitude__range=(min_lng, max_lng),
        ).only("name", "latitude", "longitude", "retail_price")

    def _select_stops(self, route_points, stations):
        stops = []
        miles_since_last_fill = 0
        last_position = route_points[0]

        for point in route_points:
            miles_since_last_fill += geodesic(
                (last_position[1], last_position[0]),
                (point[1], point[0])
            ).miles

            if miles_since_last_fill >= self.MAX_RANGE:
                cheapest = self._cheapest_near_point(point, stations)

                if cheapest:
                    stops.append({
                        "name": cheapest.name,
                        "price": cheapest.retail_price,
                        "latitude": cheapest.latitude,
                        "longitude": cheapest.longitude,
                    })

                miles_since_last_fill = 0

            last_position = point

        return stops

    def _cheapest_near_point(self, point, stations):
        lat, lng = point[1], point[0]

        nearby = []

        for station in stations:
            distance = geodesic(
                (lat, lng),
                (station.latitude, station.longitude)
            ).miles

            if distance <= 10:
                nearby.append(station)

        if not nearby:
            return None

        return min(nearby, key=lambda s: s.retail_price)

    def _calculate_cost(self, total_distance, stops):
        gallons_needed = total_distance / self.MPG

        if not stops:
            return 0

        avg_price = sum(s["price"] for s in stops) / len(stops)

        return Decimal(str(gallons_needed)) * avg_price
