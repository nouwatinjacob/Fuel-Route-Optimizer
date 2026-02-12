import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from routes.models import FuelStation
from routes.services.geocoding import GeocodingService


class Command(BaseCommand):
    help = "Load fuel stations and geocode during ingestion"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="/data/fuel-prices-for-be-assessment.csv"
        )

    def handle(self, *args, **opts):
        path = opts["file"]
        geocoder = GeocodingService()

        created = 0
        updated = 0
        skipped = 0

        self.stdout.write("Reading CSV...")

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            rows = list(reader)

        total = len(rows)
        self.stdout.write(f"{total} rows detected")

        with transaction.atomic():

            for i, row in enumerate(rows, 1):
                try:
                    obj, is_new = FuelStation.objects.get_or_create(
                        opis_id=int(row["OPIS Truckstop ID"]),
                        defaults={
                            "name": row["Truckstop Name"].strip(),
                            "address": row["Address"].strip(),
                            "city": row["City"].strip(),
                            "state": row["State"].strip(),
                            "rack_id": int(row["Rack ID"]),
                            "retail_price": float(row["Retail Price"]),
                        }
                    )

                    if is_new:
                        created += 1

                    if obj.latitude is None:
                        lat, lng = geocoder.get(obj.city, obj.state)
                        obj.latitude = lat
                        obj.longitude = lng
                        obj.save(update_fields=["latitude", "longitude"])
                        updated += 1
                    else:
                        skipped += 1

                except Exception:
                    continue

                if i % 50 == 0 or i == total:
                    self.stdout.write(
                        f"{i}/{total} processed | "
                        f"created={created} "
                        f"geocoded={updated} "
                        f"cached={skipped}"
                    )

        self.stdout.write(self.style.SUCCESS("Seeding complete"))
