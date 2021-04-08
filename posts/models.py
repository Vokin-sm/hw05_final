import textwrap

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """The 'Group' model, the object of which you can select
    when creating a post."""
    title = models.CharField('Название сообщества', max_length=200)
    slug = models.SlugField('url', unique=True)
    description = models.TextField('Описание',
                                   help_text='Опишите это сообщество')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """The 'Posts' model is needed to create posts."""
    text = models.TextField('Текст поста', help_text='Напишите ваш пост')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='groups',
                              verbose_name='Сообщество')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        return textwrap.shorten(self.text, width=15, placeholder='...')


class Comment(models.Model):
    """The 'Comment' model is needed to create comments."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='Автор')
    text = models.TextField('Текст комментария',
                            help_text='Напишите ваш комментарий')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return textwrap.shorten(self.text, width=15, placeholder='...')
