from rest_framework import serializers
from .models import Stock


class StockSerializer(serializers.ModelSerializer):
    high = serializers.DecimalField(max_digits=10, decimal_places=5, write_only=True)
    low = serializers.DecimalField(max_digits=10, decimal_places=5, write_only=True)
    change_price_percent = serializers.DecimalField(max_digits=10, decimal_places=5, write_only=True)
    change_percent = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = '__all__'
    
    def get_change_percent(self, obj: Stock):
        return str(obj.change_price_percent) + "%"
