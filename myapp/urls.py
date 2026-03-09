from django.urls import path,include
from . import views



urlpatterns =[
    path('', views.home),
    path("live/", views.live_page),
    path("rooms/", views.room_list, name="room_list"),
    path("chat/<str:room_name>/", views.chat_room, name="chat_room"),

    path("products/",views.product_list, name='product_list'),
    path("product/<int:pk>/",views.product_detail, name='product_detail'),
    path("order/create/", views.create_order,name="create_order")

]