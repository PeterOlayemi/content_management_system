from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib import messages

from .decorators import AdminRequiredMixin
from .models import *
from .forms import *
from account.models import User
from account.forms import ReaderUpdateForm, WriterUpdateForm, RegisterForm
from writer.models import Article
from writer.forms import ArticleForm
from reader.models import Comment
from reader.forms import CommentForm

# Create your views here.

class HomeView(AdminRequiredMixin, TemplateView):
    template_name = 'administrator/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_users'] = User.objects.filter(is_active=True).count()
        reader_group = Group.objects.get(name='Reader')
        context['active_readers'] = User.objects.filter(is_active=True, groups=reader_group).count()
        writer_group = Group.objects.get(name='Writer')
        context['active_writers'] = User.objects.filter(is_active=True, groups=writer_group).count()
        admin_group = Group.objects.get(name='Admin')
        context['active_admins'] = User.objects.filter(is_active=True, groups=admin_group).count()
        context['new_articles'] = Article.objects.filter(date_added__date=now().date()).count()
        context['new_comments'] = Comment.objects.filter(date_added__date=now().date()).count()
        context['logs'] = Log.objects.order_by('-date')[:10]
        context['articles'] = Article.objects.order_by('-views')[:10]
        return context

class ReaderProfileView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        logs = Log.objects.filter(user=user).order_by('-date')
        paginator = Paginator(logs, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
                    'user':user,
                    'logs':page_obj,
                    'paginator':paginator,
                }
        return render(request, 'administrator/reader_profile.html', context)

class ReaderUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = ReaderUpdateForm
    context_object_name = 'user'
    template_name = 'administrator/reader_update.html' # Redirect after successful update

    def form_valid(self, form):
        user = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated '{user.username}' profile")
        log.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Profile Updated Successfully')
        return reverse_lazy('a_reader_profile', kwargs={'pk': self.object.pk})

class ReaderDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'administrator/reader_delete.html'
    context_object_name = 'user'
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted '{user.username}' account")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'User Deleted Successfully')
        return reverse_lazy('a_manage_user')

class WriterProfileView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        published_articles = Article.objects.filter(writer=user, status='PUBLISH').order_by('-views')
        
        query = self.request.GET.get('q')
        if query:
            published_articles = published_articles.filter(
                Q(category__name__icontains=query) | Q(title__icontains=query)
            ).distinct()
            
        published_articles_paginator = Paginator(published_articles, 4)
        published_articles_page_number = self.request.GET.get('published_articles_page')
        published_articles_page_obj = published_articles_paginator.get_page(published_articles_page_number)
        
        draft_articles = Article.objects.filter(writer=user, status='DRAFT').order_by('-date_added')
        draft_articles_paginator = Paginator(draft_articles, 4)
        draft_articles_page_number = self.request.GET.get('draft_articles_page')
        draft_articles_page_obj = draft_articles_paginator.get_page(draft_articles_page_number)
        
        recent_posts = Article.objects.filter(writer=user, status='PUBLISH').order_by('-date_added')[:5]
        
        logs = Log.objects.filter(user=user).order_by('-date')
        paginator = Paginator(logs, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
                    'user':user,
                    'published_articles':published_articles,
                    'published_articles':published_articles_page_obj,
                    'search_query':self.request.GET.get('q', ''),
                    'draft_articles':draft_articles,
                    'draft_articles':draft_articles_page_obj,
                    'recent_posts':recent_posts,
                    'logs':page_obj,
                    'paginator':paginator,
                }
        return render(request, 'administrator/writer_profile.html', context)

class WriterUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = WriterUpdateForm
    context_object_name = 'user'
    template_name = 'administrator/writer_update.html' # Redirect after successful update

    def form_valid(self, form):
        user = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated '{user.username}' profile")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Profile Updated Successfully')
        return reverse_lazy('a_writer_profile', kwargs={'pk': self.object.pk})

class WriterDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'administrator/writer_delete.html'
    context_object_name = 'user'
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted '{user.username}' account")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'User Deleted Successfully')
        return reverse_lazy('a_manage_user')

class AdminProfileView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        published_articles = Article.objects.filter(writer=user, status='PUBLISH').order_by('-views')
        
        query = self.request.GET.get('q')
        if query:
            published_articles = published_articles.filter(
                Q(category__name__icontains=query) | Q(title__icontains=query)
            ).distinct()
            
        published_articles_paginator = Paginator(published_articles, 4)
        published_articles_page_number = self.request.GET.get('published_articles_page')
        published_articles_page_obj = published_articles_paginator.get_page(published_articles_page_number)
        
        draft_articles = Article.objects.filter(writer=user, status='DRAFT').order_by('-date_added')
        draft_articles_paginator = Paginator(draft_articles, 4)
        draft_articles_page_number = self.request.GET.get('draft_articles_page')
        draft_articles_page_obj = draft_articles_paginator.get_page(draft_articles_page_number)
        
        recent_posts = Article.objects.filter(writer=user, status='PUBLISH').order_by('-date_added')[:5]
        
        logs = Log.objects.filter(user=user).order_by('-date')
        paginator = Paginator(logs, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
                    'user':user,
                    'published_articles':published_articles,
                    'published_articles':published_articles_page_obj,
                    'search_query':self.request.GET.get('q', ''),
                    'draft_articles':draft_articles,
                    'draft_articles':draft_articles_page_obj,
                    'recent_posts':recent_posts,
                    'logs':page_obj,
                    'paginator':paginator,
                }
        return render(request, 'administrator/admin_profile.html', context)

class AdminUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = ReaderUpdateForm
    context_object_name = 'user'
    template_name = 'administrator/admin_update.html' # Redirect after successful update

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = self.get_object()
        log = Log(user=user, action=f"'{user.username}(Admin)' updated his/her profile")
        log.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Profile Updated Successfully')
        return reverse_lazy('a_admin_profile', kwargs={'pk': self.object.pk})

class ChangePasswordView(AdminRequiredMixin, PasswordChangeView):
    template_name = 'administrator/change_password.html'
    
    def get_success_url(self):
        user = self.request.user
        log = Log(user=user, action=f"'{user.username}(Admin)' changed his/her password")
        log.save()
        messages.success(self.request, 'Your New Password Has Been Set Successfully.')
        return reverse_lazy('a_admin_profile',  kwargs={'pk': self.request.user.pk})

class ManageUserView(AdminRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'administrator/manage_user.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True).order_by('-date_joined')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['user'] = page_obj
        context['total_users'] = queryset.count()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class UserCreateView(AdminRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'administrator/user_create.html'
    success_url = reverse_lazy('a_manage_user')

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.profile_picture:
            user.profile_picture = self.request.FILES.get('profile_picture')
        user.save()
        if user.role == 'Writer':
            writer_group, created = Group.objects.get_or_create(name='Writer')
            user.groups.add(writer_group)
        else:
            reader_group, created = Group.objects.get_or_create(name='Reader')
            user.groups.add(reader_group)
        user.save()
        admin = self.request.user
        log = Log(user=admin, action=f"'{admin.username}(Admin)' created a user - '{user.username}'")
        log.save()
        messages.success(self.request, 'New User Added Successfully')
        return super().form_valid(form)

class ManageArticleView(AdminRequiredMixin, ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'administrator/manage_article.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-date_added')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(writer__username__icontains=query) | Q(category__name__icontains=query) | Q(title__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['articles'] = page_obj
        context['paginator'] = paginator
        context['total_articles'] = queryset.count()
        context['categories'] = Category.objects.all().order_by(Lower('name'))
        context['total_categories'] = Category.objects.count()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ArticleCreateView(AdminRequiredMixin, CreateView):
    form_class = ArticleForm
    template_name = 'administrator/article_create.html'

    def form_valid(self, form):
        form.instance.writer = self.request.user
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' added an article - '{form.instance.title}'")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Article Created Successfully')
        return reverse_lazy('a_article_detail', kwargs={'pk': self.object.pk})

class ArticleDetailView(AdminRequiredMixin, View):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        number_of_likes = article.number_of_likes()
        comments = Comment.objects.filter(article=article).order_by('-date_added')
        total_comments = Comment.objects.filter(article=article).count()
        liked = False
        if article.likes.filter(id=request.user.id).exists():
            liked = True
        form = CommentForm()
        recent_posts = Article.objects.filter(writer=article.writer, status='PUBLISH').order_by('-date_added')[:5]
        return render(request, 'administrator/article_detail.html', {'article': article, 'form': form, 'number_of_likes':number_of_likes, 'comments':comments, 'total_comments':total_comments, 'article_is_liked':liked, 'recent_posts':recent_posts})

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            comment.article = article
            comment.save()
            log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' added a comment - '{comment.content}' on article - '{article.title}'")
            log.save()
            messages.success(request, 'Comment Added Successfully')
            return redirect(reverse_lazy('a_article_detail', kwargs={'pk': article.pk}))
        return render(request, 'administrator/article_detail.html', {'article': article, 'form': form})

class ArticleLikeView(AdminRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' unliked an article - '{article.title}'")
            log.save()
            messages.success(request, 'Article Unliked Successfully')
        else:
            article.likes.add(request.user)
            log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' liked an article - '{article.title}'")
            log.save()
            messages.success(request, 'Article Liked Successfully')
        return redirect(reverse_lazy('a_article_detail', kwargs={'pk': article.pk}))

class ArticleLikerView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'administrator/article_liker.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        article_id = self.kwargs.get('pk')
        article = Article.objects.get(id=article_id)
        return article.likes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        article_id = self.kwargs.get('pk')
        article = Article.objects.get(id=article_id)
        context['article'] = article
        context['number_of_likes'] = article.number_of_likes()
        return context

class ArticleUpdateView(AdminRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'administrator/article_update.html'
    context_object_name = 'article'

    def form_valid(self, form):
        article = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated an article - '{article.title}'")
        log.save()
        return super().form_valid(form)    

    def get_success_url(self):
        messages.success(self.request, 'Article Updated Successfully')
        return reverse_lazy('a_article_detail', kwargs={'pk': self.object.pk})

class ArticleDeleteView(AdminRequiredMixin, DeleteView):
    model = Article
    template_name = 'administrator/delete.html'
    context_object_name = 'article'
    
    def post(self, request, *args, **kwargs):
        article = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted an article - '{article.title}'")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Article Deleted Successfully')
        return reverse_lazy('a_manage_article')
    
class CommentUpdateView(AdminRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'administrator/article_detail.html'
    context_object_name = 'comment_to_be_updated'

    def form_valid(self, form):
        comment = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated a comment - '{comment.content}' on article - '{comment.article.title}'")
        log.save()
        return super().form_valid(form) 

    def get_success_url(self):
        messages.success(self.request, 'Comment Updated Successfully')
        return reverse_lazy('a_article_detail', kwargs={'pk': self.object.article.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = get_object_or_404(Article, pk=self.object.article.pk)
        number_of_likes = article.number_of_likes()
        comments = Comment.objects.filter(article=article).order_by('-date_added')
        total_comments = Comment.objects.filter(article=article).count()
        liked = False
        if article.likes.filter(id=self.request.user.id).exists():
            liked = True
        form = CommentForm(instance=self.object)
        
        recent_posts = Article.objects.filter(writer=article.writer, status='PUBLISH').order_by('-date_added')[:5]
        context['recent_posts'] = recent_posts
        
        context['article'] = article
        context['form'] = form
        context['number_of_likes'] = number_of_likes
        context['comments'] = comments
        context['total_comments'] = total_comments
        context['article_is_liked'] = liked
        return context

class CommentReplyView(AdminRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'administrator/article_detail.html'

    def form_valid(self, form):
        comment_to_be_replied = get_object_or_404(Comment, pk=self.kwargs['pk'])
        article = comment_to_be_replied.article
        form.instance.writer = self.request.user
        form.instance.article = article
        form.instance.parent = comment_to_be_replied
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' replied - '{form.instance.content}' on a thread - '{comment_to_be_replied.content}'")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        article = comment.article
        messages.success(self.request, 'Reply Added Successfully')
        return reverse_lazy('a_article_detail', kwargs={'pk': article.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_to_be_replied = get_object_or_404(Comment, pk=self.kwargs['pk'])
        article = comment_to_be_replied.article
        number_of_likes = article.number_of_likes()
        comments = Comment.objects.filter(article=article).order_by('-date_added')
        total_comments = Comment.objects.filter(article=article).count()
        liked = False
        if article.likes.filter(id=self.request.user.id).exists():
            liked = True
        form = CommentForm()
        
        recent_posts = Article.objects.filter(writer=article.writer, status='PUBLISH').order_by('-date_added')[:5]
        context['recent_posts'] = recent_posts
        
        context['comment_to_be_replied'] = comment_to_be_replied
        context['article'] = article
        context['form'] = form
        context['number_of_likes'] = number_of_likes
        context['comments'] = comments
        context['total_comments'] = total_comments
        context['article_is_liked'] = liked
        return context

class CommentDeleteView(AdminRequiredMixin, DeleteView):
    model = Comment
    template_name = 'administrator/delete.html'
    context_object_name = 'comment'
    
    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted a comment - '{comment.content}' on article - '{comment.article.title}'")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        article = self.object.article
        messages.success(self.request, 'Comment Deleted Successfully')
        return reverse_lazy('a_article_detail', kwargs={'pk': article.pk})

class ManageCategoryView(AdminRequiredMixin, ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'administrator/manage_category.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by(Lower('name'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['categories'] = page_obj
        context['paginator'] = paginator
        context['total_categories'] = queryset.count()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class CategoryCreateView(AdminRequiredMixin, CreateView):
    form_class = CategoryForm
    template_name = 'administrator/category_create.html'

    def form_valid(self, form):
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' added a category - '{form.instance.name}'")
        log.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Category Created Successfully')
        return reverse_lazy('a_manage_category')

class ArticleCategoryList(ListView):
    model = Article
    template_name = 'administrator/article_category_list.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        category = self.kwargs.get('category')
        queryset = super().get_queryset()
        queryset = queryset.filter(status='PUBLISH', category__name=category).order_by('-views')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(writer__username__icontains=query) | Q(title__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('category')
        category_model = Category.objects.get(name=category)
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['total_articles'] = queryset.count()
        context['category_model'] = category_model
        context['category'] = category
        context['articles'] = page_obj
        context['paginator'] = paginator
        context['search_query'] = self.request.GET.get('q', '')

        recent_posts = Article.objects.filter(status='PUBLISH', category__name=category).order_by('-date_added')[:5]
        context['recent_posts'] = recent_posts
        
        other_categories = Category.objects.exclude(name=category).order_by(Lower('name'))
        context['other_categories'] = other_categories

        if queryset:
            trending_articles = queryset.order_by('-views')[:1]
            for trending_article in trending_articles:
                trending_writer = trending_article.writer
            context['trending_writer'] = trending_writer
        return context

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'administrator/category_update.html'
    context_object_name = 'category'

    def form_valid(self, form):
        category = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated a category - '{category.name}'")
        log.save()
        return super().form_valid(form) 

    def get_success_url(self):
        messages.success(self.request, 'Category Updated Successfully')
        return reverse_lazy('a_article_category_list', kwargs={'category': self.object.name})

class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'administrator/delete.html'
    context_object_name = 'category'
    
    def post(self, request, *args, **kwargs):
        category = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted a category - '{category.name}'")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Category Deleted Successfully')
        return reverse_lazy('a_manage_category')
    
class ManageContactView(AdminRequiredMixin, DetailView):
    model = Contact
    template_name = 'administrator/manage_contact.html'
    context_object_name = 'contact'
    
    def get_object(self, queryset=None):
        return Contact.objects.first()

class ContactCreateView(AdminRequiredMixin, CreateView):
    form_class = ContactForm
    template_name = 'administrator/contact_create.html'
    
    def form_valid(self, form):
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' added the ByteWrite contact information'")
        log.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Contact Created Successfully')
        return reverse_lazy('a_manage_contact')

class ContactUpdateView(AdminRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'administrator/contact_update.html'
    context_object_name = 'contact'
    
    def form_valid(self, form):
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated the ByteWrite contact information")
        log.save()
        return super().form_valid(form) 

    def get_success_url(self):
        messages.success(self.request, 'Contact Updated Successfully')
        return reverse_lazy('a_manage_contact')

class ManageTeamView(AdminRequiredMixin, ListView):
    model = Team
    context_object_name = 'teams'
    template_name = 'administrator/manage_team.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by(Lower('full_name'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        context['total_teams'] = queryset.count()
        return context

class TeamCreateView(AdminRequiredMixin, CreateView):
    form_class = TeamForm
    template_name = 'administrator/team_create.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.image = self.request.FILES.get('image')
        obj.save()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' added to the ByteWrite Team'")
        log.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Team Member Created Successfully')
        return reverse_lazy('a_team_detail', kwargs={'pk': self.object.pk})

class TeamDetailView(AdminRequiredMixin, DetailView):
    model = Team
    template_name = 'administrator/team_detail.html'
    context_object_name = 'team'

class TeamUpdateView(AdminRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'administrator/team_update.html'
    context_object_name = 'team'
    
    def form_valid(self, form):
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' updated a ByteWrite Team Member Information")
        log.save()
        return super().form_valid(form) 
    
    def get_success_url(self):
        messages.success(self.request, 'Team Member Updated Successfully')
        return reverse_lazy('a_team_detail', kwargs={'pk': self.object.pk})

class TeamDeleteView(AdminRequiredMixin, DeleteView):
    model = Team
    template_name = 'administrator/delete.html'
    context_object_name = 'team'
    
    def post(self, request, *args, **kwargs):
        log = Log(user=self.request.user, action=f"'{self.request.user.username}(Admin)' deleted a team member")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Team Member Deleted Successfully')
        return reverse_lazy('a_manage_team')
    
class ManageLogView(AdminRequiredMixin, ListView):
    model = Log
    context_object_name = 'logs'
    template_name = 'administrator/manage_log.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query) | Q(action__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['logs'] = page_obj
        context['paginator'] = paginator
        context['search_query'] = self.request.GET.get('q', '')
        return context
