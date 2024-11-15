from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='reader_home'),
    path('articles/<category>/', ArticleCategoryList.as_view(), name='reader_article_category_list'),
    path('profile/r/<int:pk>/', ReaderProfileView.as_view(), name='reader_profile'),
    path('profile/w/<int:pk>/', WriterProfileView.as_view(), name='writer_profile'),
    path('profile/a/<int:pk>/', AdminProfileView.as_view(), name='admin_profile'),
    path('profile/update/', ReaderUpdateView.as_view(), name='reader_update'),
    path('password/change/', ChangePasswordView.as_view(), name='reader_change_password'),
    path('article/detail/<int:pk>/', ArticleDetailView.as_view(), name='reader_article_detail'),
    path('article/like/<int:pk>/', ArticleLikeView.as_view(), name='reader_article_like'),
    path('comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='reader_comment_delete'),
    path('comment/update/<int:pk>/', CommentUpdateView.as_view(), name='reader_comment_update'),
    path('comment/reply/<int:pk>/', CommentReplyView.as_view(), name='reader_reply_comment'),
]
