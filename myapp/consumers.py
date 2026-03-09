from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Room, Message,Product,Order
import datetime

class LiveMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Websocket connected")
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        message = message + " Munim"

        await self.send(json.dumps({
            "message" : f"Typed: {message}"
        }))


    async def disconnect(self, close_code):
        print("❌ WebSocket disconnected")


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group = f"chat_{self.room_name}"

        self.user = self.scope["user"]
        

        if not self.user.is_authenticated:
            await self.close()
            return
        
        await self.accept()
        
        self.room = await self.get_room()
        
        
        in_room = await self.is_user_in_room()
        if not in_room:
          await self.close()
          return
        
        messages = await self.get_last_messages()

        for msg in reversed(messages):
           await self.send(text_data=json.dumps({
              "user": msg.user.username,
              "message": msg.content,
             "timestamp": msg.timestamp.isoformat()
           }))
        
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

       

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )

    async def receive(self, text_data = None):
        try:
          data = json.loads(text_data)
        except json.JSONDecodeError:
          return
        message = data.get("message", "").strip()

        if not message:
          return

        await self.save_message(message)
        

        from django.utils.timezone import now

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
                "timestamp": now().isoformat(),
                
            }
        )

    async def chat_message(self,event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user" : event["user"],
            "timestamp": event["timestamp"]
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
          .select_related("user").order_by('-timestamp')[:50]
       )
       
    
    @database_sync_to_async
    def save_message(self, message):
        Message.objects.create(room = self.room,
                               user = self.user,
                               content = message)
    


from django.db import transaction

class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope["url_route"]["kwargs"]["product_id"]
        self.product_group = f"product_{self.product_id}"

        await self.channel_layer.group_add(
            self.product_group,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.product_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        qty = int(data.get("quantity", 1))

        try:
            stock = await self.create_order(qty)
            await self.channel_layer.group_send(
                self.product_group,
                {
                    "type": "stock_update",
                    "stock": stock
                }
            )
        except ValueError as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    @database_sync_to_async
    def create_order(self, qty):
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=self.product_id)

            if product.stock < qty:
                raise ValueError("Not enough stock")

            product.stock -= qty
            product.save(update_fields=["stock"])

            Order.objects.create(
                product=product,
                quantity=qty
            )

            return product.stock

    async def stock_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "stock_update",
            "stock": event["stock"]
        }))
      


class StockConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "stock_updates",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            "stock_updates",
            self.channel_name
        )

    async def stock_update(self, event):
        await self.send(text_data=json.dumps({
            "product_id": event["product_id"],
            "stock": event["stock"]
        }))
      
   

