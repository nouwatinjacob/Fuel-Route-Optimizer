from django.core.management.base import BaseCommand
from routes.models import FuelStation
from routes.services.geocoding import GeocodingService


class Command(BaseCommand):
    help = "Geocode fuel stations missing coordinates"

    def handle(self, *args, **kwargs):
        geocoder = GeocodingService()

        qs = FuelStation.objects.filter(latitude__isnull=True)
        total = qs.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No stations missing coordinates"))
            return

        self.stdout.write(f"{total} stations need geocoding")

        for i, station in enumerate(qs, 1):
            lat, lng = geocoder.get(station.city, station.state)

            station.latitude = lat
            station.longitude = lng
            station.save(update_fields=["latitude", "longitude"])

            if i % 20 == 0 or i == total:
                self.stdout.write(f"{i}/{total} processed")

        self.stdout.write(self.style.SUCCESS("Geocode missing completed"))
