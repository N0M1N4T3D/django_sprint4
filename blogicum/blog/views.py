from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.utils.timezone import now
from .models import Post, Category, User, Comment
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Count



class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('category').annotate(comment_count=Count('comments')).filter(
            is_published=True, category__is_published=True,
            pub_date__lte=now()).order_by('-pub_date')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all().order_by('created_at')
        context['form'] = CommentForm()
        return context

class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(Category, is_published=True, slug=self.kwargs['category_slug'])
        return Post.objects.filter(category=category, is_published=True, pub_date__lte=now()).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, is_published=True, slug=self.kwargs['category_slug'])
        return context

class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class EditProfileView(UpdateView):
    model = User  # Указываем модель User
    form_class = UserChangeForm
    template_name = 'blog/user.html'

    @method_decorator(login_required)  # Ensure user is logged in before submitting a comment
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self, queryset=None):
        # Получаем текущего пользователя
        return self.request.user

    def get_success_url(self):
        # Перенаправляем на страницу профиля после успешного сохранения
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})
    
class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    @method_decorator(login_required)  # Убедитесь, что пользователь авторизован
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user  # Устанавливаем текущего пользователя как автора поста
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})



class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    @method_decorator(login_required)  # Убедитесь, что пользователь авторизован
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post  # Устанавливаем пост для комментария
        form.instance.author = self.request.user  # Устанавливаем текущего пользователя как автора комментария
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})


class EditCommentView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    @method_decorator(login_required)  # Ensure user is logged in before submitting a comment
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'], post__id=self.kwargs['post_id'])
        # Проверяем, что комментарий принадлежит текущему пользователю
        if comment.author != self.request.user:
            return None  # Возвращаем None, если комментарий не принадлежит пользователю
        return comment

    def form_valid(self, form):
        # Убедитесь, что автор комментария не меняется
        form.instance.author = self.request.user  # Устанавливаем текущего пользователя как автора
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})



class DeleteCommentView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    @method_decorator(login_required)  # Ensure user is logged in before submitting a comment
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'], post__id=self.kwargs['post_id'])
        # Проверяем, что комментарий принадлежит текущему пользователю
        if comment.author != self.request.user:
            return None
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})


class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    @method_decorator(login_required)  # Ensure user is logged in before submitting a comment
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        # Проверяем, что пост принадлежит текущему пользователю
        if post.author != self.request.user:
            return None
        return post

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.id})

class DeletePostView(DeleteView):
    model = Post
    template_name = 'blog/create.html'

    @method_decorator(login_required)  # Ensure user is logged in before submitting a comment
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        # Проверяем, что пост принадлежит текущему пользователю
        if post.author != self.request.user:
            return None
        return post

    def get_success_url(self):
        # Перенаправляем на страницу профиля после успешного удаления
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})