from django.urls import path,include
from . import views



urlpatterns =[
    path('', views.home),
   
    path("rooms/", views.room_list, name="room_list"),
    path("chat/<str:room_name>/", views.chat_room, name="chat_room"),


]