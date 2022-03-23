from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .models import Author, Category, Post, PostCategory, SubUser
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.core.mail import send_mail, EmailMultiAlternatives, mail_admins
from django.views import View
from .filters import PostFilter
from .forms import PostForm
from .forms import PostDeleteForm
from django.contrib.auth.decorators import login_required, permission_required
from celery import shared_task



EMAIL_LINK_DOMAIN = 'http://127.0.0.1:8000' #Das ist ein Scheiß Platz. Das sollte Zentraler..aber für erst mal reicht es

# Dekorator, wird von app.autodiscover_tasks() in celery.py gesucht
@shared_task
def SubscriberNotificationMail(): # Einfache Methode ohne Argumente
    for category in Category.objects.all(): # Eine Schleife, die durch alle vorhandenen Artikelkategorien läuft
        Posts=Post.objects.filter(postCategory=category) # Alle Posts die zu dieser Kategorie gehören
        # Achtung, bei den Posts fehlt noch der Filter "maximal eine Woche alt", aber darauf scheißen wir erst mal
        subject = f' Ihre Abos' # Betreff der email
        subscriber = category.get_subscriber_mail_adresses() # Methode die alle Subscriber dieser Kategorie zurückliefert
        # email inhalt, das was subscriber bekommt
        html_content = render_to_string( # Hier wird die html gerendert
            'flatpages/subscription_email_postlist_by_category.html',
            {
                'posts': Posts, #Eine Liste mit Posts die zu der Kategorie gehören
                'category': category, # Die Kategorie
                'email_link_domain': EMAIL_LINK_DOMAIN # Die Angabe, wie der Benutzer die url erreicht. Also /news -> www.annas-supernews.ru/news
            }
        )
        msg = EmailMultiAlternatives( # das Ding bastlt die emails zusammen für jeden Subscriber
            subject=subject, # Text wird oben generiert (Betreff)
            to=subscriber,  # это то же, что и recipients_list
        )

        msg.attach_alternative(html_content, "text/html")  # добавляем html Die html, die oben generiert wird
        print("Wöchentliche email gesendet") # Damit man sieht, dass das Ding was tut
        msg.send()  # отсылаем Uuuuuuuuuuuund weg, die 'ure


# Das ganze Ding müssen wir uns noch mal komplett angucken
# ich habe keine Ahnung, wie das funktioniert
class PostList(ListView): # Die Übersichstsseite mit den Artikeln
    model = Post # Referenz auf das Modell
    template_name = 'flatpages/news.html' # Angabe des Template
    context_object_name = 'posts' #  Oh fuck, Maus, das müssen wir uns echt noch mal angucken
    queryset = Post.objects.order_by('-dateCreation') #Alle Posts, geordnet nach Erstellungsdatum
    paginate_by = 3 # Attribut für deinen Paginator - Anzahl der Artikel pro Seite
    from_class = PostForm  # No idea
    def get_filter(self):#wtf
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):#wtf
        return self.get_filter().qs  # ruft die Methode auf, suchen nach Stichwörter dees Titles.

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['time_now'] = datetime.utcnow()
        context['categorys'] = Category.objects.all()  # ch
        context['form'] = PostForm()
        return context

# Müssen wir uns auch noch mal bezüglich der inneren Logik anschauen
class PostDetail(DetailView): # Auch Akrakadabra
    model = Post # Klar
    template_name = 'flatpages/new.html' # Klar
    context_object_name = 'post' # pfff
    queryset = Post.objects.all()  #

# Dekorator, dass der AKTUELLE Benutzer das überhaupt aufrufen darf
# HTML kennt (scheinbar) zwei Methoden. POST und GET.
# GET ist, wenn die Seite das erste Mal aufgerufen wird.
# Also so ziemlich immer.
# POST wird aufgerufen, wenn der Datenfluss umgekehrt ist.
# Der Benutzer also irgendwelche Daten hoch lädt.
@permission_required('news.add_post', '/accounts/login/', True)
def post_create(request):
    if request.method == 'POST': #Abfrage, welche Sorte die Anfrage ist
        form = PostForm(request.POST)
        if form.is_valid(): # Überprüfung, ob die Daten gültig sind
            form.save() #Speichern in der Datenbank
            return redirect('post_create') # Umleitung auf die Dankeschön Page
    else:
        form = PostForm() # Wenn es die erste Anfage ist, anzeigen des Formulars
    return render(request, # Rendern ist aus Daten eine Anzeige machen
                  'flatpages/post_create.html', # Vorlage
                  {
                      'form': form # Übergabe der form als Parameter. Das ganze Prinzip müssen wir uns noch mal anschauen
                  })

#Gleicher Scheiß wie oben
@permission_required('news.change_post', '/accounts/login/', True)
def post_edit(request, pk=None):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_create')
    else:
        form = PostForm(instance=post)

    return render(request,
                  'flatpages/post_edit.html',
                  {
                      'form': form,
                      'post': post
                  })


# Ebenfalls
@permission_required('news.delete_post', '/accounts/login/', True)
def post_delete(request, pk=None):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostDeleteForm(request.POST,
                              instance=post)
        if form.is_valid():
            post.delete()
            return redirect('post_create')
    else:
        form = PostDeleteForm(instance=post)

    return render(request, 'flatpages/post_delete.html',
                  {
                      'form': form,
                      'post': post,
                  })


# Müssen wir uns auch noch mal angucken
# Wie funktioniert die Interaktion zwischen views und forms
class SubUserView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'flatpages/subscribe.html', {})

    def post(self, request, *args, **kwargs):
        category_name = request.POST['category_name']
        category = Category.objects.get(name=category_name)

        subscription = SubUser(
            sub_user=request.user,
            category=category,
            # user_email = email,
        )

        subscription.save()

        html_content = render_to_string(
            'flatpages/subscription_created.html',
            {
                'subscription': subscription,
                'email_link_domain': EMAIL_LINK_DOMAIN
            }
        )
        msg = EmailMultiAlternatives(
            subject=f'Ihr Abbonement',
            # body=email.message,  # это то же, что и message
            # from_email='nura.auxutat@yandex.ru',
            to=[request.user.email],  # это то же, что и recipients_list
        )

        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем

        return redirect('')

@receiver(user_signed_up) #Wie oben
def user_signed_up_(sender, request, user, **kwargs):
    subject, from_email, to = 'Willkommen. Sie haben sich erfolgreich bei News angemeldet.', 'nura.auxutat@yandex.ru', user.email
    html_content = render_to_string(
        'flatpages/user_signed_up_create.html',
        {
            'email_link_domain': EMAIL_LINK_DOMAIN
        }
    )
    msg = EmailMultiAlternatives(subject,"some text" , from_email, [to])
    msg.attach_alternative(html_content, "text/html")  # добавляем html
    msg.send()
