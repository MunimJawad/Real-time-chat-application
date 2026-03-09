from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order


@receiver(post_save, sender=Order)
def update_stock(sender, instance, created, **kwargs):
    if not created:
        return

    product = instance.product

    
    product.stock -= instance.quantity
    product.save(update_fields=["stock"])

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "stock_updates",
        {
            "type": "stock_update",
            "product_id": product.id,
            "stock": product.stock,
        }
    )
