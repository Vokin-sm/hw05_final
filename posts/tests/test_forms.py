import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

from . import constants as c

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username=c.USERNAME_IVANOV)
        cls.image = SimpleUploadedFile(
            name='test.gif',
            content=c.test_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=PostFormTests.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        self.post_id = Post.objects.get(
            text='Тестовый текст',
            author=PostFormTests.user).pk

    def test_create_post(self):
        """Проверяет, что валидная форма создает запись в Post
        и работает redirect."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'image': PostFormTests.image
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверяет, что редактирование поста через
        форму на странице /<username>/<post_id>/edit/
        изменяет соответствующую запись в базе данных."""
        form_data = {
            'text': 'изменённый пост',
        }
        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': c.USERNAME_IVANOV,
                            'post_id': self.post_id}),
            data=form_data, follow=True)
        post = Post.objects.get(author=PostFormTests.user,
                                pk=self.post_id)
        self.assertRedirects(
            response, reverse('post',
                              kwargs={'username': c.USERNAME_IVANOV,
                                      'post_id': self.post_id}))
        self.assertEqual(post.text, 'изменённый пост')
