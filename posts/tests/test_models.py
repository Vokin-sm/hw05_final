import textwrap

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

from . import constants as c

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=c.SLUG,
            description='Тестовое описание сообщества'
        )

    def test_description_label(self):
        """verbose_name поля description совпадает с ожидаемым."""
        group = GroupModelTest.group
        verbose = group._meta.get_field('description').verbose_name
        self.assertEquals(verbose, 'Описание')

    def test_description_help_text(self):
        """help_text поля description совпадает с ожидаемым."""
        group = GroupModelTest.group
        help_text = group._meta.get_field('description').help_text
        self.assertEquals(help_text, 'Опишите это сообщество')

    def test_object_name_is_description_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=c.USERNAME_IVANOV)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostModelTest.user
        )

    def test_text_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст поста')

    def test_text_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Напишите ваш пост')

    def test_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.title."""
        post = PostModelTest.post
        expected_object_name = textwrap.shorten(
            post.text, width=15, placeholder='...')
        self.assertEquals(expected_object_name, str(post))
