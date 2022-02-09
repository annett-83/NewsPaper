from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.validators import MinValueValidator
from datetime import datetime


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    # пропуск одна строка
    def update_rating(self):  # рализовать через for
        postRat = self.post_set.all().aggregate(
            postRating=Sum('rating'))  # получаем значения из поля рэйтинг класса Post
        pRat = 0
        pRat += postRat.get('postRating')  # выводим результат подсчета

        # тоже самое с коментариями
        commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')
        # подсчитываем рейтинг автора и сохраняем
        self.ratingAuthor = pRat * 3 + cRat
        self.save()

    # пропук 2 строки

    def __str__(self):
        return self.authorUser.username + ' ' + self.authorUser.last_name


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)  # значения max_length берут как 2 в  степени
    subscriber = models.ManyToManyField(User, through='SubUser')

    def get_subscriber_mail_adresses(self): # Methode die alle Benutzer-emails sucht, die diese Kategorie abbobiert haben
        a = User.objects.filter(category=self).values_list('email', flat=True).distinct()
        return list(a)

    def __str__(self):
        return self.name


class SubUser(models.Model):
    sub_user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Nachrichten'),
        (ARTICLE, 'Artikel'),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)  # автоиатически выставл. врея поста
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()  # ohne Begrenzung
    quantity = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0, 'Quantity should be >=0')]
                                   )  # 8/12 change
    rating = models.SmallIntegerField(default=0)

    def _str_(self):
        return f'{self.post}{self.quantity}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'  # в больших проектах использовать форматирование что бы экономить память

    def get_absolute_url(self):
        from django.urls import reverse  # sucht uel yum object seldst
        return reverse('article', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title} {self.text}'

    def get_edit_url(self):
        from django.urls import reverse
        return reverse('post_edit', kwargs={'pk': self.pk})

    def get_delete_url(self):
        from django.urls import reverse
        return reverse('post_delete', kwargs={'pk': self.pk})
    # def get_absolute_urx(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
    #     return f'/post/{self.id}'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)  # автоиатически выставл. врея поста
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1  # суммируем полож.отзывы
        self.save()

    def dislike(self):
        self.rating -= 1  # отнимаем от полож.отзывы
        self.save()


class Appointment(models.Model):  # Termin machen
    date = models.DateField(
        default=datetime.utcnow,
    )
    client_name = models.CharField(
        max_length=200
    )
    message = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'
