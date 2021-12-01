from django.views.generic import ListView, DetailView
from.models import Author, Category,Post,PostCategory
from datetime import datetime

class PostList(ListView):
    model = Post
    template_name = 'flatpages/news.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()  # добавим переменную текущей даты time_now
        return context

class PostDetail(DetailView):
    model=Post
    template_name = 'flatpages/new.html'
    context_object_name = 'post'


