from django.core.mail import mail_managers
from django.core.mail import send_mail, EmailMultiAlternatives, mail_admins
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post, PostCategory, Category
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from .views import EMAIL_LINK_DOMAIN

@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_managers_post(sender, instance, action, *args, **kwargs):
    pk_category_ids = kwargs['pk_set']
    if action == "post_add":
        for pk_category_id in pk_category_ids:
            category = Category.objects.get(pk=pk_category_id)
            subject = f' Ein Artikel wurde hinzugefügt'
            subscriber=category.get_subscriber_mail_adresses()
            html_content = render_to_string(
                'flatpages/subscription_email_post_modified.html',
                {
                    'post': instance,
                    'category' : category,
                    'email_link_domain' : EMAIL_LINK_DOMAIN
                }
            )
            msg = EmailMultiAlternatives(
                subject=subject,
                # body=email.message,  # это то же, что и message
                # from_email='nura.auxutat@yandex.ru',
                to=subscriber,  # это то же, что и recipients_list
            )

            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()  # отсылаем
