from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils import timezone
from .models import Post, Category, User, Comment
from .forms import CommentForm, UserForm
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.db.models import Count


class PostBaseMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'location', 'category', 'image']

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class RedirectToPostMixin:
    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('category').annotate(
            comment_count=Count('comments')).filter(
            is_published=True, category__is_published=True,
            pub_date__lte=now()).order_by('-pub_date')


class PostDetailView(PostBaseMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return get_object_or_404(
                Post.objects.filter(
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now()
                ), id=self.kwargs[self.pk_url_kwarg]
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'comments': self.get_object().comments.all(),
            'form': CommentForm(),
        })
        return context


class CommentChangeMixin(RedirectToPostMixin):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category, is_published=True, slug=self.kwargs['category_slug'])
        return Post.objects.filter(
            category=category, is_published=True,
            pub_date__lte=now()).order_by('-pub_date').annotate(
                comment_count=Count('comments'))


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user).order_by(
            '-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


@method_decorator(login_required, name='dispatch')
class EditProfileView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username.username})


@method_decorator(login_required, name='dispatch')
class CreatePostView(PostBaseMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, id=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


@method_decorator(login_required, name='dispatch')
class EditPostView(PostBaseMixin, UpdateView):
    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[
            self.kwargs[self.pk_url_kwarg]])


class DeletePostView(LoginRequiredMixin, PostBaseMixin, DeleteView):
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
