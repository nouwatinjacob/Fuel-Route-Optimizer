from django.db import models

# Create your models here.
class FuelStation(models.Model):
    """Model representing a fuel/truck stop with pricing information."""
    
    opis_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=2, db_index=True)
    rack_id = models.IntegerField()
    retail_price = models.DecimalField(max_digits=10, decimal_places=8)
    
    latitude = models.FloatField(null=True, blank=True, db_index=True)
    longitude = models.FloatField(null=True, blank=True, db_index=True)
    
    class Meta:
        db_table = 'fuel_stations'
        indexes = [
            models.Index(fields=['state', 'city']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['retail_price']),
        ]
        ordering = ['retail_price']
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state} (${self.retail_price}/gal)"
    
    @property
    def location_dict(self):
        """Return location as dictionary."""
        return {
            'lat': self.latitude,
            'lng': self.longitude
        }
