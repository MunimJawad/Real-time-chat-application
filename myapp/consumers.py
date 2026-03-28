from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Room, Message, UserPresence
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group = f"chat_{self.room_name}"

        self.user = self.scope["user"]
        

        if not self.user.is_authenticated:
            await self.close()
            return
        
        await database_sync_to_async(UserPresence.objects.update_or_create)(
            user=self.user,
            defaults={"is_online": True, "last_seen": datetime.datetime.now()}
        )
        
        await self.accept()
        
        self.room = await self.get_room()
        
        
        in_room = await self.is_user_in_room()
        if not in_room:
          await self.close()
          return
        
        messages = await self.get_last_messages()

        for msg in reversed(messages):
           presence = getattr(msg.user, "userpresence", None)
           await self.send(text_data=json.dumps({
              "user": msg.user.username,
              "message": msg.content,
              "online_status": presence.is_online if presence else False,
             "timestamp": msg.timestamp.isoformat()
           }))
        
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

       
    from django.utils import timezone
    async def disconnect(self, code):
        user = self.scope["user"]
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )
        await database_sync_to_async(UserPresence.objects.filter(user=user).update)(
            is_online=False,
            last_seen = self.timezone.now()
        )


    async def receive(self, text_data = None):
        try:
          data = json.loads(text_data)
        except json.JSONDecodeError:
          return
        
        #Handle typing indicator
        msg_typing = data.get("type")
        if msg_typing == "typing":
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type":"typing_indicator",
                    "user": self.user.username
                }
            )
            return
        
        #normal chat message
        message = data.get("message", "").strip()

        if not message:
          return

        message = await self.save_message(message)
        
        presence = await database_sync_to_async(UserPresence.objects.filter(user=self.user).first)()
        from django.utils.timezone import now

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "message": message.content,
                "message_id": message.id,
                "online_status": presence.is_online if presence else False,
                "user": self.user.username,
                "timestamp": now().isoformat(),
                
            }
        )

    async def typing_indicator(self,event):
        if event["user"] == self.user.username:
          return  # don't show your own typing
        await self.send(text_data=json.dumps({
            "typing": event["user"]
        }))    

    async def chat_message(self,event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            'message_id': event["message_id"],
            "user" : event["user"],
            "timestamp": event["timestamp"],
            "online_status": event["online_status"]
        }))
    
    @database_sync_to_async
    def get_room(self):
        return Room.objects.filter(name = self.room_name).first()
    
    @database_sync_to_async
    def is_user_in_room(self):
       return self.room.users.filter(id=self.user.id).exists()
    
    @database_sync_to_async
    def get_last_messages(self):
       return list(
          Message.objects.filter(room=self.room)
          .select_related("user", "user__userpresence").order_by('-timestamp')[:50]
       )
       
    
    @database_sync_to_async
    def save_message(self, message):
        message = Message.objects.create(room = self.room,
                               user = self.user,
                               content = message)
        
        return message
    


