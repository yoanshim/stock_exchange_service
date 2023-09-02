from django.urls import path
from stock_exchange import views


urlpatterns = [
    path('stock/<str:symbol>/', views.get_stock, name='get_stock'),
    path('cost', views.get_total_cost, name='get_total_cost'),
    path('cost/reset', views.reset_counter, name='get_total_cost'),
]
