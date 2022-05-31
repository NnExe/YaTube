from django import forms

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image', )
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Группа, к которой будет относиться пост'}


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description', )
        help_texts = {'title': 'Короткое название',
                      'slug': 'slug-строка, которая может быть частью адреса',
                      'description': 'Полное описание группы'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Введите текст комментария'}
