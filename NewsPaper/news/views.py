import form as form
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from.models import Author, Category,Post,PostCategory
from datetime import datetime
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.core.paginator import Paginator
from .filters import PostFilter
from .forms import PostForm
from .forms import PostDeleteForm
from django.contrib.auth.decorators import login_required, permission_required

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

    # def post(self,request,*args,**kwargs):#ch
    #     form=self.form_class(request.POST)
    #
    #     if form.is_valid():
    #         form.save()
    #
    #     return super().get(request,*args,**kwargs)


class PostDetail(DetailView):
    model=Post
    template_name = 'flatpages/new.html'
    context_object_name = 'post'
    queryset = Post.objects.all()#

#@login_required(login_url='/accounts/login/') #18/12
@permission_required('news.add_post','/accounts/login/',True)
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


#@login_required(login_url='/accounts/login/') #18/12
@permission_required('news.change_post','/accounts/login/',True)
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


#@login_required(login_url='/accounts/login/') #18/12
@permission_required('news.delete_post','/accounts/login/',True)
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


