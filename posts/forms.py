from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Form class for creating a new post."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Сообщество не выбрано'

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentsForm(forms.ModelForm):
    """Comments class for creating a new comment."""

    class Meta:
        model = Comment
        fields = ('text',)
