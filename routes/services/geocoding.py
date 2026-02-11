from django.core.cache import cache
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


class GeocodingService:
    """
    Responsible ONLY for translating a (city, state) into coordinates.

    Features:
    - Rate limiting (OpenStreetMap policy compliant)
    - Long-term caching (geocoding should be treated as immutable)
    - Provider abstraction (easy to swap later)
    """

    CACHE_PREFIX = "geocode:"
    CACHE_TIMEOUT = 60 * 60 * 24 * 365  # 1 year

    def __init__(self):
        geolocator = Nominatim(user_agent="fuel_route_loader")
        self._geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    def _cache_key(self, city: str, state: str) -> str:
        return f"{self.CACHE_PREFIX}{city.lower()}||{state.lower()}"

    def get_coordinates(self, city: str, state: str) -> tuple[float | None, float | None]:
        """
        Returns (lat, lng). Uses cache before hitting provider.
        """
        key = self._cache_key(city, state)
        cached = cache.get(key)

        if cached is not None:
            return cached

        query = f"{city}, {state}, USA"

        try:
            location = self._geocode(query)

            if location:
                coords = (location.latitude, location.longitude)
            else:
                coords = (None, None)

        except Exception:
            coords = (None, None)

        cache.set(key, coords, timeout=self.CACHE_TIMEOUT)
        return coords
