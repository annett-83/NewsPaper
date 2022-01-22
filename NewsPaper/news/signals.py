from django.core.mail import mail_managers
from django.db.models.signals import post_save
from django.dispatch import receiver  # импортируем нужный декоратор

from .models import Post


@receiver(post_save, sender=Post)
def notify_managers_Post(sender, instance, created, **kwargs):
    if created:
        subject = f'{instance.subscription} {instance.date.strftime("%d %m %Y")}'
    else:
        subject = f'Benachrichtigung für {instance.subscription} {instance.date.strftime("%d %m %Y")}'

    mail_managers(
        subject=subject,
        message=instance.message,
    )
    # das sieht doch toll aus aber nichs funktioniert
