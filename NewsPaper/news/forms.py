from django.forms import ModelForm
from .models import Post, SubUser


# Создаём модельную форму
class PostForm(ModelForm):
    # в класс мета, как обычно, надо написать модель, по которой будет с
# троится форма и нужные нам поля. Мы уже делали что-то похожее с фильтрами.
    class Meta:
        model = Post
        #fields = ['author','text','']
        exclude=['rating','quantity', 'dateCreation']

class PostDeleteForm(ModelForm):
    class Meta:
        model = Post
        fields= []

class SubscribeForm(ModelForm):
    class Meta:
        model= SubUser
        fields= []
