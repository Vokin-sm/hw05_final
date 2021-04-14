import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

from . import constants as c

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(
            username=c.USERNAME_IVANOV)
        cls.another_user = User.objects.create_user(
            username=c.USERNAME_PETROV)
        cls.group = Group.objects.create(
            title='Тестовое название сообщества',
            slug=c.SLUG,
            description='Тестовое описание сообщества'
        )
        cls.empty_group = Group.objects.create(
            title='Пустая группа',
            slug=c.SLUG_EMPTY_GROUP,
            description='Описание пустой группы'
        )
        cls.image = SimpleUploadedFile(
            name='test.gif',
            content=c.test_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            text='Текст поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.image
        )
        Follow.objects.create(user=PostPagesTests.user,
                              author=PostPagesTests.another_user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(
            PostPagesTests.another_user)
        self.post_id = Post.objects.get(
            text='Текст поста',
            author=PostPagesTests.user).pk
        self.number_of_posts = Post.objects.filter(
            author=PostPagesTests.user).count()
        self.context_content = {
            'selected_user': PostPagesTests.user,
            'current_user': PostPagesTests.user}

    def test_pages_use_correct_template(self):
        """Проверяет какой шаблон будет вызван при обращении
        к view-функциям через соответствующее имя."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': c.SLUG})
            ),
            'new.html': reverse('new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_list_page_list_is_1(self):
        """Проверяет, что на страницу со списком постов передаётся
        ожидаемое количество объектов."""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            len(response.context['page']), 1)

    def test_posts_list_page_show_correct_context(self):
        """Проверяет, что шаблон index сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_image_0.name, 'posts/test.gif')

    def test_group_pages_show_correct_context(self):
        """Проверяет, что шаблон group сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': c.SLUG})
        )
        self.assertEqual(
            response.context['page'][0].text,
            'Текст поста'
        )
        self.assertEqual(
            response.context['page'][0].author,
            PostPagesTests.user
        )
        self.assertEqual(
            response.context['page'][0].image.name,
            'posts/test.gif'
        )
        self.assertEqual(
            response.context['group'].title,
            'Тестовое название сообщества'
        )
        self.assertEqual(
            response.context['group'].description,
            'Тестовое описание сообщества'
        )

    def test_new_group_show_correct_context(self):
        """Проверяет, что шаблон new сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_empty_group_show_correct_context(self):
        """Проверяет, что пост не попал в группу,
        для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': c.SLUG_EMPTY_GROUP})
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_username_post_id_edit_correct_context(self):
        """Проверяет содержимое словаря context
        страницы /<username>/<post_id>/edit/"""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': c.USERNAME_IVANOV,
                                         'post_id': self.post_id})
        )
        group = Post.objects.get(pk=self.post_id).group
        form_fields_content = {
            response.context['form'].initial['text']: 'Текст поста',
            group.title: PostPagesTests.group.title
        }
        for value, expected in form_fields_content.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_username_correct_context(self):
        """Проверяет содержимое словаря context
        страницы /<username>/"""
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': c.USERNAME_IVANOV})
        )
        for value, expected in self.context_content.items():
            with self.subTest(value=value):
                context_field = response.context[value]
                self.assertEqual(context_field, expected)
        self.assertEqual(
            response.context['page'][0].text,
            'Текст поста'
        )
        self.assertEqual(
            response.context['page'][0].author,
            PostPagesTests.user
        )
        self.assertEqual(
            response.context['page'][0].image.name,
            'posts/test.gif'
        )

    def test_username_post_id_correct_context(self):
        """Проверяет содержимое словаря context
        страницы /<username>/<post_id>/"""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': c.USERNAME_IVANOV,
                            'post_id': self.post_id})
        )
        for value, expected in self.context_content.items():
            with self.subTest(value=value):
                context_field = response.context[value]
                self.assertEqual(context_field, expected)
        self.assertEqual(
            response.context['selected_post'].text,
            'Текст поста'
        )
        self.assertEqual(
            response.context['selected_post'].author,
            PostPagesTests.user
        )
        self.assertEqual(
            response.context['selected_post'].image.name,
            'posts/test.gif'
        )

    def test_count_posts_page(self):
        """Проверяет, что в словарь context
        главной страницы передаётся не более
        установленного количества постов."""
        for _ in range(15):
            Post.objects.create(
                text='Текст поста',
                author=PostPagesTests.user,
                group=PostPagesTests.group
            )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            len(response.context['page']), 10)

    def test_page_index_cache(self):
        """Проверяет, что на главной странице
        работает Cache"""
        content_one_post = self.authorized_client.get(reverse('index')).content
        Post.objects.create(
            text='Текст второго поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.image
        )
        content_two_post = self.authorized_client.get(reverse('index')).content
        self.assertEqual(content_one_post, content_two_post)

    def test_profile_follow(self):
        """Проверяет, что Авторизованный пользователь
        может подписываться на других пользователей"""
        follow_count = Follow.objects.filter(
            user=PostPagesTests.another_user).count()
        self.another_authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': c.USERNAME_IVANOV}
                    ))
        self.assertEqual(Follow.objects.filter(
            user=PostPagesTests.another_user).count(), follow_count + 1)

    def test_profile_unfollow(self):
        """Проверяет, что Авторизованный пользователь
        может отписываться от других пользователей"""
        follow_count = Follow.objects.filter(
            user=PostPagesTests.user).count()
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': c.USERNAME_PETROV}
                    ))
        self.assertEqual(Follow.objects.filter(
            user=PostPagesTests.user).count(), follow_count - 1)

    def test_follow_index(self):
        """Проверяет, что новая запись пользователя появляется в
        ленте тех, кто на него подписан и не появляется в ленте
        тех, кто не подписан на него."""
        Post.objects.create(
            text='Другой текст поста',
            author=PostPagesTests.another_user)
        response = self.authorized_client.get(
            reverse('follow_index'))
        self.assertEqual(
            len(response.context['page']), 1)
        response = self.another_authorized_client.get(
            reverse('follow_index'))
        self.assertEqual(
            len(response.context['page']), 0)
