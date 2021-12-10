from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from.models import Author, Category,Post,PostCategory
from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from .filters import PostFilter
from .forms import PostForm#


class PostList(ListView):
    model = Post
    template_name = 'flatpages/news.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 1
    from_class=PostForm#

    def get_filter(self):
        return PostFilter(self.request.GET,queryset=super().get_queryset())
    def get_queryset(self):
        return self.get_filter().qs #rufen die Metode auf, suchen nach Stichwörter dees Titles.

    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data(*args,**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['time_now'] = datetime.utcnow()
        context['categorys'] = Category.objects.all()#ch
        context['form'] = PostForm()
        return context
def post(self,request,*args,**kwargs):#ch
    form=self.form_class(request.POST)

    if form.is_valid():
        form.save()

    return super().get(request,*args,**kwargs)




class PostDetail(DetailView):
    model=Post
    template_name = 'flatpages/new.html'
    context_object_name = 'post'
    queryset = Post.objects.all()#

class PostCreateView(CreateView):#
    template_name='flatpages/post_create.html'
    form_class=PostForm


# дженерик для редактирования объекта
class PostUpdateView(UpdateView):
    template_name = 'flatpages/post_create.html'
    form_class = PostForm

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDeleteView(DeleteView):
    template_name = 'flatpages/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/post/'


