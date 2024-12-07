from django import forms
from .models import Post, Comment, User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'location', 'image'] 


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)