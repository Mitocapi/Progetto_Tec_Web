from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

def home(request):
    return render(request, template_name="home.html")

class UserCreateView(CreateView):
    form_class = CreaUtenteCliente()
    template_name = "user_create.html"
    success_url = reverse_lazy("login")


class FotografoCreateView(PermissionRequiredMixin, UserCreateView):
    permission_required = "is_staff"
    form_class = CreaUtenteFotografo

