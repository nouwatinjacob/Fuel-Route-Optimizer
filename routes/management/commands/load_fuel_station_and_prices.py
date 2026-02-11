from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from routes.models import FuelStation
from routes.services.geocoding import GeocodingService
from routes.services.fuel_loader import FuelStationCSVLoader


class Command(BaseCommand):
    help = "Load fuel stations from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--geocode", action="store_true")

    def handle(self, *args, **options):
        should_geocode = options["geocode"]

        loader = FuelStationCSVLoader(settings.FUEL_DATA_PATH)
        rows = loader.load()

        self.stdout.write(f"Loaded {len(rows)} rows")

        geocoder = GeocodingService() if should_geocode else None

        stations = []

        for row in rows:
            lat, lng = (None, None)

            if geocoder:
                lat, lng = geocoder.get_coordinates(row.city, row.state)

            stations.append(
                FuelStation(
                    opis_id=row.opis_id,
                    name=row.name,
                    address=row.address,
                    city=row.city,
                    state=row.state,
                    rack_id=row.rack_id,
                    retail_price=row.retail_price,
                    latitude=lat,
                    longitude=lng,
                )
            )

        with transaction.atomic():
            FuelStation.objects.all().delete()
            FuelStation.objects.bulk_create(stations, batch_size=1000)

        self.stdout.write(self.style.SUCCESS("Fuel stations loaded successfully"))
