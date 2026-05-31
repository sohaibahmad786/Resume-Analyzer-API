from django.db.models.signals import post_save
from django.dispatch import receiver
from Api.models import Booking, Notification


@receiver(post_save, sender=Booking)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message="Your booking is confirmed"
        )
