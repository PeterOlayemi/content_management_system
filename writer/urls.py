from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='writer_home'),
    path('articles/<category>/', ArticleCategoryList.as_view(), name='writer_article_category_list'),
    path('profile/r/<int:pk>/', ReaderProfileView.as_view(), name='w_reader_profile'),
    path('profile/w/<int:pk>/', WriterProfileView.as_view(), name='w_writer_profile'),
    path('profile/a/<int:pk>/', AdminProfileView.as_view(), name='w_admin_profile'),
    path('profile/update/', WriterUpdateView.as_view(), name='writer_update'),
    path('password/change/', ChangePasswordView.as_view(), name='writer_change_password'),
    path('article/create/', ArticleCreateView.as_view(), name='writer_article_create'),
    path('article/detail/<int:pk>/', ArticleDetailView.as_view(), name='writer_article_detail'),
    path('article/like/<int:pk>/', ArticleLikeView.as_view(), name='writer_article_like'),
    path('article/liker/<int:pk>/', ArticleLikerView.as_view(), name='writer_article_liker'),
    path('article/delete/<int:pk>/', ArticleDeleteView.as_view(), name='writer_article_delete'),
    path('article/update/<int:pk>/', ArticleUpdateView.as_view(), name='writer_article_update'),
    path('comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='writer_comment_delete'),
    path('comment/update/<int:pk>/', CommentUpdateView.as_view(), name='writer_comment_update'),
    path('comment/reply/<int:pk>/', CommentReplyView.as_view(), name='writer_reply_comment'),
]
