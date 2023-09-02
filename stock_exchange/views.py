import requests
import datetime
from django.utils.timezone import now, timedelta
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import api_view
from stock_exchange.models import Stock
from stock_exchange.serializers import StockSerializer
from stock_exchange_server.settings import ALPHA_QUOTE_URL, COST_ALPHA_API_CALL


def fetch_stock_from_third_party_api(symbol):
    url = f"{ALPHA_QUOTE_URL}&symbol={symbol}"
    response = requests.get(url)
    try:
        response.raise_for_status()
        data = response.json()["Global Quote"]
        stock_data = dict(
            symbol=data["01. symbol"],
            high=data["03. high"],
            low=data["04. low"],
            price=data["05. price"],
            change_price_percent=data['10. change percent'].replace("%", "")
        )
        curr_counter = cache.get("total_api_counter", 0)
        cache.set("total_api_counter", curr_counter+1)
    except requests.HTTPError as http_err:
        # Handle specific cases based on status codes or other criteria if needed
        print(f"fetch stock third party HTTP error occurred: {http_err}")
        raise
    except Exception as e:
        print(f"fetch stock third party generalerror occurred: {e}")
        raise

    return stock_data


def update_stock(symbol, stock=None):
    updated_data = fetch_stock_from_third_party_api(symbol)
    serializer = StockSerializer(instance=stock, data=updated_data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


@api_view(["GET"])
def get_stock(request, symbol):
    symbol = symbol.upper()
    try:
        stock = Stock.objects.get(symbol=symbol)
    except Stock.DoesNotExist:
        data = update_stock(symbol)
        return Response(data)

    current_time = now().time()

    if current_time >= datetime.time(10, 0) and current_time <= datetime.time(
        17, 0
    ):  # Trading hours
        price_move = stock.high / stock.low

        if price_move > 1.03:  # More than 3% move in price
            max_age = timedelta(minutes=10)
        else:
            max_age = timedelta(minutes=20)
    else:
        max_age = timedelta(hours=1)

    if now() - stock.update_time > max_age:
        data = update_stock(symbol, stock)
        return Response(data)

    serializer = StockSerializer(stock)
    return Response(serializer.data)

@api_view(["GET"])
def get_total_cost(request):
    total_counter = cache.get("total_api_counter", 0)
    total_cost = total_counter * COST_ALPHA_API_CALL
    return Response(str(total_cost) + "$")

@api_view(["POST"])
def reset_counter(request):
    cache.set("total_api_counter", 0)
    return Response("counter reset succeed")