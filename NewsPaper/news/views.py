from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .models import Author, Category, Post, PostCategory, Appointment, SubUser
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


class PostList(ListView):
    model = Post
    template_name = 'flatpages/news.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 1
    from_class = PostForm  #

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs  # rufen die Metode auf, suchen nach Stichwörter dees Titles.

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['time_now'] = datetime.utcnow()
        context['categorys'] = Category.objects.all()  # ch
        context['form'] = PostForm()
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'flatpages/new.html'
    context_object_name = 'post'
    queryset = Post.objects.all()  #

# @login_required(login_url='/accounts/login/') #18/12

@permission_required('news.add_post', '/accounts/login/', True)
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_create')
    else:
        form = PostForm()
    return render(request,
                  'flatpages/post_create.html',
                  {
                      'form': form
                  })


# @login_required(login_url='/accounts/login/') #18/12
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


# @login_required(login_url='/accounts/login/') #18/12
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


# @login_required(login_url='/accounts/login/') #18/12
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

@receiver(user_signed_up)
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
        # send_mail(
        # subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
        #     # имя клиента и дата записи будут в теме для удобства
        #     message=appointment.message,  # сообщение с кратким описанием проблемы
        #   from_email='nura.auxutat@yandex.ru',
        #     # здесь указываете почту, с которой будете отправлять (об этом попозже)
        # recipient_list=['ann.auksutat@yandex.ru']  # здесь список получателей. Например, секретарь, сам врач и т. д.
        # )
        #
        # # получаем наш html
        # html_content = render_to_string(
        #     'flatpages/appointment_created.html',
        #     {
        #         'appointment': appointment,
        #     }
        # )
        #
        # # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
        # msg = EmailMultiAlternatives(
        #     subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
        #     body=appointment.message,  # это то же, что и message
        #     from_email='nura.auxutat@yandex.ru',
        #     to=['ann.auksutat@yandex.ru'],  # это то же, что и recipients_list
        # )
        # msg.attach_alternative(html_content, "text/html")  # добавляем html
        #
        # msg.send()  # отсылаем
        # # отправляем письмо всем админам по аналогии с send_mail, только здесь получателя указывать не надо
        # mail_admins(
        #     subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
        #     message=appointment.message,
        # )
        # return redirect('make_appointment')
        #


# class AppointmentView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'flatpages/appointment.html', {})
#
#     def post(self, request, *args, **kwargs):
#         appointment = Appointment(
#             date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
#             client_name=request.POST['client_name'],
#             message=request.POST['message'],
#         )
#         appointment.save()
#
#         # отправляем письмо
#         send_mail(
#             subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
#             # имя клиента и дата записи будут в теме для удобства
#             message=appointment.message,  # сообщение с кратким описанием проблемы
#             from_email='nura.auxutat@yandex.ru',
#             # здесь указываете почту, с которой будете отправлять (об этом попозже)
#             recipient_list=['ann.auksutat@yandex.ru']  # здесь список получателей. Например, секретарь, сам врач и т. д.
#         )
#
#         # получаем наш html
#         html_content = render_to_string(
#             'flatpages/appointment_created.html',
#             {
#                 'appointment': appointment,
#             }
#         )
#
#         # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
#         msg = EmailMultiAlternatives(
#             subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
#             body=appointment.message,  # это то же, что и message
#             from_email='nura.auxutat@yandex.ru',
#             to=['ann.auksutat@yandex.ru'],  # это то же, что и recipients_list
#         )
#         msg.attach_alternative(html_content, "text/html")  # добавляем html
#
#         msg.send()  # отсылаем
#         # отправляем письмо всем админам по аналогии с send_mail, только здесь получателя указывать не надо
#         mail_admins(
#             subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
#             message=appointment.message,
#         )
#         return redirect('make_appointment')

# class PostCreateView(LoginRequiredMixin, CreateView):#
#     template_name ='flatpages/post_create.html'
#     form_class = PostForm
#     success_url = reverse_lazy('home')
#     login_url = reverse_lazy('home')
#     #raise_exception = True# zeigt fehler403
#
#
# # дженерик для редактирования объекта
# class PostUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = 'flatpages/post_create.html'
#     form_class = PostForm
#     success_url = reverse_lazy('home')
#     login_url = reverse_lazy('home')
#
#     # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
#     def get_object(self, **kwargs):
#         id = self.kwargs.get('pk')
#         return Post.objects.get(pk=id)
#
#
# # дженерик для удаления товара
# class PostDeleteView(LoginRequiredMixin, DeleteView):
#     template_name = 'flatpages/post_delete.html'
#     queryset = Post.objects.all()
#     success_url = reverse_lazy('post')
#     login_url = reverse_lazy('home')
