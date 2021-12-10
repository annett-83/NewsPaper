from django.urls import path
from .views import PostList, PostDetail,PostCreateView, PostUpdateView, PostDeleteView

urlpatterns = [
    path('',PostList.as_view(), name=''),
    path('article/<int:pk>', PostDetail.as_view(), name='article'),
    path('create/', PostCreateView.as_view(),name='post_create'),
    path('create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
]

#urlpatterns = [
    #path('',PostList.as_view()),
    #path('<int:pk>', PostDetail.as_view()),
#]