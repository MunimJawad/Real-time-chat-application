from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Room,Message,Product,Order, UserPresence


def home(request):
    return HttpResponse("Hello World")




def room_list(request):
    user = request.user
    rooms = Room.objects.filter(users = user)
    
    return render(request, 'myapp/rooms.html',
                  {
                      "rooms": rooms
                  })

def chat_room(request, room_name):
    room = get_object_or_404(Room, name=room_name)

    if request.user not in room.users.all():
        return HttpResponse("Unauthorized")
    online_status = UserPresence.objects.filter(user=request.user).first()
    messages = Message.objects.filter(room=room)

    return render(request, 'myapp/chat.html', {
        'online_status': online_status,
        "room": room,
        "messages": messages,
        "current_user": request.user  # Pass the current logged-in user
    })

