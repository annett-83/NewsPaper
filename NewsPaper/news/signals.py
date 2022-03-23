from django.core.mail import send_mail, EmailMultiAlternatives, mail_admins
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post, PostCategory, Category
from django.template.loader import render_to_string
from .views import EMAIL_LINK_DOMAIN

 #Diese Methode ist interessant, weil etwas komplexer
 #Sie wird aufgerufen, wenn die Mitteltabelle zwischen Post und Kategorie geändert wird
 #(n:m Ralation)
 #Also beispielsweise in Post hinzugefügt wird (Aber auch, wenn die Kategorie gändert wird
@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_managers_post(sender, instance, action, *args, **kwargs):
    pk_category_ids = kwargs['pk_set'] # Hier werden aus den Argumenten die Schlüssel der Kategorien ermittelt
    #Ein Post kann ja zu mehreren Kategorien gehören
    if action == "post_add": # Wenn hinzugefügt wird
        for pk_category_id in pk_category_ids: # Hier werden alle Kategorien, die ermittelt wurden durchlaufen
            category = Category.objects.get(pk=pk_category_id) # Die Aktuelle Kategorie der Schleife als Objekt
            subject = f' Ein Artikel wurde hinzugefügt' # Betreff
            subscriber=category.get_subscriber_mail_adresses() # Ermittelung aller Subscriber der Kategorie
            html_content = render_to_string( # Erstellen der email
                'flatpages/subscription_email_post_modified.html',
                {
                    'post': instance, # Der aktuelle Post
                    'category' : category, # die aktuelle Kategorie
                    'email_link_domain' : EMAIL_LINK_DOMAIN # der Link zur Domain
                }
            )
            msg = EmailMultiAlternatives( # Zusammebasteln der Mail
                subject=subject,
                # body=email.message,  # это то же, что и message
                # from_email='nura.auxutat@yandex.ru',
                to=subscriber,  # это то же, что и recipients_list
            )

            msg.attach_alternative(html_content, "text/html")  # добавляем html

            msg.send()  # отсылаем und weg damit
