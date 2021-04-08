from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import PAGINATE_BY

from .forms import CommentsForm, PostForm
from .models import Comment, Group, Post

User = get_user_model()


def index(request):
    """This function displays the main page with posts."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    """This function displays the community page with posts."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    """This function displays a page with a form to add a new post."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    """This function displays the user's profile page."""
    selected_user = get_object_or_404(User, username=username)
    current_user = request.user
    posts = Post.objects.filter(author=selected_user)
    number_of_posts = len(posts)
    paginator = Paginator(posts, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'page': page,
                   'selected_user': selected_user,
                   'number_of_posts': number_of_posts,
                   'current_user': current_user}
                  )


def post_view(request, username, post_id):
    """This function displays the user's post page."""
    selected_user = get_object_or_404(User, username=username)
    current_user = request.user
    posts = Post.objects.filter(author=selected_user)
    number_of_posts = len(posts)
    selected_post = get_object_or_404(Post, author=selected_user, pk=post_id)
    comments = Comment.objects.filter(post=selected_post)
    form = CommentsForm(request.POST or None)
    if form and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = selected_post
        comment.save()
        return redirect('post',
                        username=selected_user.username,
                        post_id=selected_post.id
                        )
    return render(request, 'post.html',
                  {'selected_user': selected_user,
                   'current_user': current_user,
                   'selected_post': selected_post,
                   'number_of_posts': number_of_posts,
                   'comments': comments,
                   'form': form
                   }
                  )


@login_required
def post_edit(request, username, post_id):
    """This function displays the user post edit page."""
    selected_user = get_object_or_404(User, username=username)
    current_user = request.user
    if current_user.username != selected_user.username:
        return redirect('profile',
                        username=selected_user.username)
    selected_post = get_object_or_404(Post,
                                      author=selected_user,
                                      pk=post_id)
    post_editing = True
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=selected_post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post',
                            username=selected_user.username,
                            post_id=post_id)

    return render(
        request, 'new.html', {'form': form,
                              'post_editing': post_editing},
    )


def page_not_found(request, exception):
    """Displays the page 'Page Not Found'."""
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    """Displays the "server error" page."""
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    selected_user = get_object_or_404(User, username=username)
    selected_post = get_object_or_404(Post, author=selected_user, pk=post_id)
    comments = Comment.objects.filter(post=selected_post)
    form = CommentsForm(request.POST or None)
    if form and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = selected_post
        comment.save()
        return redirect('add_comment',
                        username=selected_user.username,
                        post_id=selected_post.id
                        )
    return render(request, 'include/comments.html',
                  {'comments': comments,
                   'form': form})