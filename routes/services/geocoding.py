import time
from django.core.cache import cache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from geopy.extra.rate_limiter import RateLimiter


class GeocodingService:
    """
    Production-safe geocoder for bulk ingestion.

    Features:
    - long timeout (network safe)
    - exponential retry
    - Redis caching (1 year)
    - never raises fatal error
    - safe for thousands of requests
    """

    CACHE_PREFIX = "geo:"
    CACHE_TIMEOUT = 60 * 60 * 24 * 365  # 1 year
    MAX_RETRIES = 4

    def __init__(self):
        geolocator = Nominatim(user_agent="fuel_optimizer_seed")

        self._geocode = RateLimiter(
            geolocator.geocode,
            min_delay_seconds=1,
            swallow_exceptions=True,
        )

    def _cache_key(self, city: str, state: str) -> str:
        return f"{self.CACHE_PREFIX}{city.lower().strip()}:{state.lower().strip()}"

    def get_coordinates(self, city: str, state: str) -> tuple[float | None, float | None]:
        key = self._cache_key(city, state)

        cached = cache.get(key)
        if cached is not None:
            return cached

        query = f"{city}, {state}, USA"

        for attempt in range(self.MAX_RETRIES):
            try:
                location = self._geocode(query, timeout=15)

                if location:
                    coords = (location.latitude, location.longitude)
                else:
                    coords = (None, None)

                cache.set(key, coords, timeout=self.CACHE_TIMEOUT)
                return coords

            except (GeocoderTimedOut, GeocoderUnavailable):
                sleep_time = 5 * (attempt + 1)
                print(f"[Geocode retry] {query} in {sleep_time}s")
                time.sleep(sleep_time)

        print(f"[Geocode failed permanently] {query}")
        cache.set(key, (None, None), timeout=self.CACHE_TIMEOUT)
        return None, None
