from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)
#пропуск одна строка
    def update_rating(self): #рализовать через for
        postRat = self.post_set.aggregate(postRating=Sum('rating')) # получаем значения из поля рэйтинг класса Post
        pRat = 0
        pRat += postRat.get('postRating') # выводим результат подсчета
#тоже самое с коментариями
        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')
        # подсчитываем рейтинг автора и сохраняем
        self.ratingAuthor = pRat * 3 + cRat
        self.save()
# пропук 2 строки

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True) #значения max_length берут как 2 в  степени


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True) #автоиатически выставл. врея поста
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField() # ohne Begrenzung
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...' #в больших проектах использовать форматирование что бы экономить память


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
        self.rating += 1 #суммируем полож.отзывы
        self.save()

    def dislike(self):
        self.rating -= 1 #отнимаем от полож.отзывы
        self.save()



# Create your models here.