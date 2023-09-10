from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from APPfoto.models import Foto
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

def home(request):
    recent_photos = Foto.objects.order_by('-creation_date')[:5]  # 5 FOTO PIÙ NUOVE NEL CAROSELLO
    context = {'recent_photos': recent_photos}
    return render(request, 'home.html', context)
class UserCreateView(CreateView):
    form_class = CreaUtenteCliente()
    template_name = "user_create.html"
    success_url = reverse_lazy("login")


class FotografoCreateView(PermissionRequiredMixin, UserCreateView):
    permission_required = "is_staff"
    form_class = CreaUtenteFotografo

