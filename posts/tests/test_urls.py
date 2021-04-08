from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

from . import constants as c

User = get_user_model()


class AllURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=c.USERNAME_IVANOV)
        cls.another_user = User.objects.create_user(
            username=c.USERNAME_PETROV)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=AllURLTests.user
        )
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=c.SLUG,
            description='Тестовое описание сообщества'
        )

    def setUp(self):
        self.post_id = Post.objects.get(
            text='Тестовый пост',
            author=AllURLTests.user).pk
        self.guest_client = Client()
        self.authorized_client = Client()
        self.another_authorized_client = Client()
        self.authorized_client.force_login(
            AllURLTests.user)
        self.another_authorized_client.force_login(
            AllURLTests.another_user)
        self.urls_name_guest_client = [
            '/', f'/group/{c.SLUG}/',
            f'/{c.USERNAME_IVANOV}/',
            f'/{c.USERNAME_IVANOV}/{self.post_id}/']
        self.urls_name_authorized_client = [
            '/new/',
            f'/{c.USERNAME_IVANOV}/{self.post_id}/edit/'
        ]

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        for url in self.urls_name_guest_client:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ и /<username>/<post_id>/edit/
        доступна авторизованному пользователю."""
        for url in self.urls_name_authorized_client:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_username_post_id_edit_exists_at_desired_location(self):
        """Страница редактирования поста /<username>/<post_id>/edit/
        переправляет авторизованного пользователя, но не автора поста,
        на страницу /<username>/"""
        response = self.another_authorized_client.get(
            f'/{c.USERNAME_IVANOV}/{self.post_id}/edit/',
            follow=True)
        self.assertRedirects(
            response, f'/{c.USERNAME_IVANOV}/')

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new/ и /<username>/<post_id>/edit/
        перенаправит анонимного пользователя на страницу логина.
        """
        for url in self.urls_name_authorized_client:
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/group/{c.SLUG}/': 'group.html',
            '/new/': 'new.html',
            f'/{c.USERNAME_IVANOV}/{self.post_id}/edit/': 'new.html',
            f'/{c.USERNAME_IVANOV}/{self.post_id}/': 'post.html',
            f'/{c.USERNAME_IVANOV}/': 'profile.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        """Проверяет, возвращает ли сервер код 404,
        если страница не найдена."""
        response = self.guest_client.get(c.PATH_404)
        self.assertEqual(response.status_code, 404)
