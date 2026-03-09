from django.urls import path
from .consumers import LiveMessageConsumer, ChatConsumer, ProductConsumer,StockConsumer

websocket_urlpatterns = [
    path("ws/live/", LiveMessageConsumer.as_asgi()),
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
    path("ws/product/<int:product_id>/", ProductConsumer.as_asgi()),
    path("ws/stock/", StockConsumer.as_asgi()),
]
