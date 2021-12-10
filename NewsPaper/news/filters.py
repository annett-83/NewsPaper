from django_filters import FilterSet
from.models import Post, Author

class PostFilter(FilterSet):

    class Meta:
        model = Post
        fields = {
            'title':['icontains'],
            'dateCreation':['date'],
            'author':['exact'],
        }#  Filtrclasse um die Suche zu difinieren



