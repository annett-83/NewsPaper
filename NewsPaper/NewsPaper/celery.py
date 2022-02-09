import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')
app = Celery('NewsPaper')  # Prüfen Benennung
app.config_from_object('django.conf:settings', namespace='CELERY')  # Übernahme der Parameter aus den Settings
app.autodiscover_tasks()  # Celery soll alles nach Tasks durchsuchen
app.conf.beat_schedule = {  # Struktur Plan für Aufruf der Tasks
    'send_mail_every_monday_8am': { #Name der Task
        'task': 'news.views.SubscriberNotificationMail',  # Parameter. Der Name ist der Pfad zur Task
        'schedule': crontab(hour=8, minute=0, day_of_week='monday') # Definition Terminplan
    },
}
