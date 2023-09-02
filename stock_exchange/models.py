from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    update_time = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    change_price_percent = models.DecimalField(max_digits=5, decimal_places=4, help_text="Change in percentage")

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super(Stock, self).save(*args, **kwargs)
    
    def reset_counter(self):
        self.counter = 0
        self.save()
        
    def __str__(self):
        return self.symbol
