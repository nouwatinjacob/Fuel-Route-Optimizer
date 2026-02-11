import csv
from pathlib import Path


class FuelStationRow:
    """
    Lightweight domain object representing one CSV row.
    Keeps parsing separate from Django models.
    """

    def __init__(self, data: dict):
        self.opis_id = int(data["OPIS Truckstop ID"])
        self.name = data["Truckstop Name"].strip()
        self.address = data["Address"].strip()
        self.city = data["City"].strip()
        self.state = data["State"].strip()
        self.rack_id = int(data["Rack ID"])
        self.retail_price = float(data["Retail Price"])


class FuelStationCSVLoader:
    """
    Responsible only for reading + validating CSV data.
    """

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[FuelStationRow]:
        rows = []

        with open(self.path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for raw in reader:
                try:
                    rows.append(FuelStationRow(raw))
                except (ValueError, KeyError):
                    # skip bad rows — ingestion should be resilient
                    continue

        return rows

    @staticmethod
    def unique_locations(rows: list[FuelStationRow]) -> set[tuple[str, str]]:
        return {(r.city, r.state) for r in rows}
