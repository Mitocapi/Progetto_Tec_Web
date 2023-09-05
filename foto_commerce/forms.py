from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

class CreaUtenteCliente(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Clienti")
        g.user_set.add(user)
        return user


class CreaUtenteFotografo(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="Fotografi")
        g.user_set.add(user)
        return user
