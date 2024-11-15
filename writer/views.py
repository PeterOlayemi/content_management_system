from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView

from .decorators import WriterRequiredMixin
from .models import *
from .forms import *
from reader.models import *
from reader.forms import *
from account.forms import *
from administrator.models import *

# Create your views here.

class HomeView(WriterRequiredMixin, ListView):
    model = Article
    template_name = 'writer/home.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status='PUBLISH').order_by('-date_added')
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
        
        slides = Article.objects.filter(status='PUBLISH').order_by('?')[:4]
        context['slides'] = slides
        
        trending_articles = Article.objects.filter(status='PUBLISH').order_by('-views')
        context['trending_articles'] = trending_articles
        return context

class ArticleCategoryList(ListView):
    model = Article
    template_name = 'writer/article_category_list.html'
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
        
        queryset = self.get_queryset()
        paginator = Paginator(queryset, 6)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['total_articles'] = queryset.count()
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

class ReaderProfileView(WriterRequiredMixin, View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        context = {
                    'user':user,
                }
        return render(request, 'writer/reader_profile.html', context)

class WriterProfileView(WriterRequiredMixin, View):
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
        
        context = {
                    'user':user,
                    'published_articles':published_articles,
                    'published_articles':published_articles_page_obj,
                    'search_query':self.request.GET.get('q', ''),
                    'draft_articles':draft_articles,
                    'draft_articles':draft_articles_page_obj,
                    'recent_posts':recent_posts,
                }
        return render(request, 'writer/writer_profile.html', context)

class AdminProfileView(WriterRequiredMixin, View):
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
        
        recent_posts = Article.objects.filter(writer=user, status='PUBLISH').order_by('-date_added')[:5]
        
        context = {
                    'user':user,
                    'published_articles':published_articles,
                    'published_articles':published_articles_page_obj,
                    'search_query':self.request.GET.get('q', ''),
                    'recent_posts':recent_posts,
                }
        return render(request, 'writer/admin_profile.html', context)

class WriterUpdateView(WriterRequiredMixin, UpdateView):
    model = User
    form_class = WriterUpdateForm
    template_name = 'writer/user_update.html' # Redirect after successful update

    def get_object(self):
        # Get the currently logged-in user
        return self.request.user

    def form_valid(self, form):
        user = self.get_object()
        log = Log(user=user, action=f"'{user.username}' updated his/her profile")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Profile Updated Successfully')
        return reverse_lazy('w_writer_profile', kwargs={'pk': self.object.pk})

class ChangePasswordView(WriterRequiredMixin, PasswordChangeView):
    template_name = 'writer/change_password.html'
    
    def get_success_url(self):
        user = self.request.user
        log = Log(user=user, action=f"'{user.username}' changed his/her password")
        log.save()
        messages.success(self.request, 'Your New Password Has Been Set Successfully.')
        return reverse_lazy('w_writer_profile',  kwargs={'pk': self.request.user.pk})

class ArticleCreateView(WriterRequiredMixin, CreateView):
    form_class = ArticleForm
    template_name = 'writer/article_create.html'

    def form_valid(self, form):
        form.instance.writer = self.request.user
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' added an article - '{form.instance.title}'")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Article Created Successfully')
        return reverse_lazy('writer_article_detail', kwargs={'pk': self.object.pk})

class ArticleDetailView(WriterRequiredMixin, View):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user != article.writer:
            article.views += 1
            article.save()
        number_of_likes = article.number_of_likes()
        comments = Comment.objects.filter(article=article).order_by('-date_added')
        total_comments = Comment.objects.filter(article=article).count()
        liked = False
        if article.likes.filter(id=request.user.id).exists():
            liked = True
        form = CommentForm()
        recent_posts = Article.objects.filter(writer=article.writer, status='PUBLISH').order_by('-date_added')[:5]
        return render(request, 'writer/article_detail.html', {'article': article, 'form': form, 'number_of_likes':number_of_likes, 'comments':comments, 'total_comments':total_comments, 'article_is_liked':liked, 'recent_posts':recent_posts})

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            comment.article = article
            comment.save()
            log = Log(user=self.request.user, action=f"'{self.request.user.username}' added a comment - '{comment.content}' on article - '{article.title}'")
            log.save()
            messages.success(request, 'Comment Added Successfully')
            return redirect(reverse_lazy('writer_article_detail', kwargs={'pk': article.pk}))
        return render(request, 'writer/article_detail.html', {'article': article, 'form': form})

class ArticleLikeView(WriterRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            log = Log(user=self.request.user, action=f"'{self.request.user.username}' unliked an article - '{article.title}'")
            log.save()
            messages.success(request, 'Article Unliked Successfully')
        else:
            article.likes.add(request.user)
            log = Log(user=self.request.user, action=f"'{self.request.user.username}' liked an article - '{article.title}'")
            log.save()
            messages.success(request, 'Article Liked Successfully')
        return redirect(reverse_lazy('writer_article_detail', kwargs={'pk': article.pk}))

class ArticleLikerView(WriterRequiredMixin, ListView):
    model = User
    template_name = 'writer/article_liker.html'
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

class ArticleDeleteView(WriterRequiredMixin, DeleteView):
    model = Article
    template_name = 'writer/delete.html'
    context_object_name = 'article'
    
    def post(self, request, *args, **kwargs):
        article = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' deleted an article - '{article.title}'")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Article Deleted Successfully')
        return reverse_lazy('writer_home')
    
class ArticleUpdateView(WriterRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'writer/article_update.html'
    context_object_name = 'article'
    
    def form_valid(self, form):
        article = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' updated an article - '{article.title}'")
        log.save()
        return super().form_valid(form)    

    def get_success_url(self):
        messages.success(self.request, 'Article Updated Successfully')
        return reverse_lazy('writer_article_detail', kwargs={'pk': self.object.pk})

class CommentDeleteView(WriterRequiredMixin, DeleteView):
    model = Comment
    template_name = 'writer/delete.html'
    context_object_name = 'comment'
    
    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' deleted a comment - '{comment.content}' on article - '{comment.article.title}'")
        log.save()
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        article = self.object.article
        messages.success(self.request, 'Comment Deleted Successfully')
        return reverse_lazy('writer_article_detail', kwargs={'pk': article.pk})

class CommentUpdateView(WriterRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'writer/article_detail.html'
    context_object_name = 'comment_to_be_updated'

    def form_valid(self, form):
        comment = self.get_object()
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' updated a comment - '{comment.content}' on article - '{comment.article.title}'")
        log.save()
        return super().form_valid(form) 

    def get_success_url(self):
        messages.success(self.request, 'Comment Updated Successfully')
        return reverse_lazy('writer_article_detail', kwargs={'pk': self.object.article.pk})

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

class CommentReplyView(WriterRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'writer/article_detail.html'

    def form_valid(self, form):
        comment_to_be_replied = get_object_or_404(Comment, pk=self.kwargs['pk'])
        article = comment_to_be_replied.article
        form.instance.writer = self.request.user
        form.instance.article = article
        form.instance.parent = comment_to_be_replied
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' replied - '{form.instance.content}' on a thread - '{comment_to_be_replied.content}'")
        log.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        article = comment.article
        messages.success(self.request, 'Reply Added Successfully')
        return reverse_lazy('writer_article_detail', kwargs={'pk': article.pk})

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
