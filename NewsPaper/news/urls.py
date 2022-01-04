from django.urls import path
from .views import PostList, PostDetail,post_create, post_delete, post_edit  # PostCreateView, PostUpdateView, PostDeleteView



urlpatterns = [
    path('',PostList.as_view(), name=''),
    path('post/<int:pk>', PostDetail.as_view(), name='article'),
    path('article/create/', post_create, name='post_create'),
    path('article/delete/<int:pk>/', post_delete, name='post_delete'),
    path('article/edit/<int:pk>/', post_edit, name='post_edit'),
    #path('create/', PostCreateView.as_view(),name='post_create'),
    # path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    # path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
]

#urlpatterns = [
    #path('',PostList.as_view()),
    #path('<int:pk>', PostDetail.as_view()),
#]