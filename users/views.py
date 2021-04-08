from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Class for displaying a page with a form for registering a new user."""
    form_class = CreationForm
    success_url = reverse_lazy('signup')
    template_name = 'signup.html'
