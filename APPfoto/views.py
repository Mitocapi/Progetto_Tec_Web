from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import SearchForm
from django.shortcuts import render
from django.views import View
from django.db.models import Count, Exists, OuterRef, Q
from django.core.paginator import Paginator


def home_view(request):
    return render(request, template_name="APPfotoTempl/home.html")



class FotografiListView(ListView):
    template_name = 'APPfotoTempl/lista_fotografi.html'
    context_object_name = 'members'

    def get_queryset(self):
        fotografi_group = Group.objects.get(name='Fotografi')
        members = User.objects.filter(groups=fotografi_group).annotate(
            positive_review_count=Count('recensioni', filter=Q(recensioni__voto_positivo=True))
        )

        # Check the 'sort' query parameter and apply sorting
        sort_by = self.request.GET.get('sort')
        if sort_by == 'positive_reviews':
            members = members.order_by('-positive_review_count')
        elif sort_by == 'alphabetical':
            members = members.order_by('username')

        return members

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_name'] = 'Fotografi'
        return context


class SearchWrongColourView(View):
    template_name = "APPfotoTempl/search_wrong_colour.html"

    def get(self, request, *args, **kwargs):
        form = SearchForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if request.method == "POST":
            form = SearchForm(request.POST)
            if form.is_valid():
                sstring = form.cleaned_data.get("search_string")
                where = form.cleaned_data.get("search_where")
                return redirect("APPfoto:ricerca_risultati", sstring, where)
            else:
                context = {'form': form}
            return render(request, self.template_name, context)


class FotoListView(ListView):
    titolo="Abbiamo trovato queste foto"
    model = Foto
    template_name = "APPfotoTempl/lista_foto.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort', None)


        # Sort the queryset based on the sort_by parameter
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == 'new':
            queryset = queryset.order_by('creation_date')

        return queryset


def Asearch(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            sstring = form.cleaned_data.get("search_string")
            where = form.cleaned_data.get("search_where")
            print("PRINTO WHERE DAL SEARCH: " + where)
            return redirect("APPfoto:ricerca_risultati", sstring, where)

    else:
        form = SearchForm()

    return render(request, "APPfotoTempl/search.html", context= {"form": form})

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_where = form.cleaned_data['search_where']
            print("PRIMO WHERE = " + search_where)
            sstring = form.cleaned_data['search_string']

            if not sstring.strip():
                # Handle the case when searching by artist and sstring is empty
                sstring = 'No name specified'

            # Redirect to the results page with the selected search criteria
            print(search_where)
            print(sstring)
            return redirect("APPfoto:ricerca_risultati", sstring=sstring, where=search_where)

    else:
        form = SearchForm()
    return render(request, 'APPfotoTempl/search.html', {'form': form})


class FotoListaRicercataView(FotoListView):
    titolo = "risultati ricerca"

    def get_queryset(self):
        queryset = super().get_queryset()
        where = self.request.GET.get('where')
        print(where)

        # Sort the queryset based on the sort_by parameter
        sort = self.request.GET.get('sort')
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == 'new':
            queryset = queryset.order_by('-creation_date')

        # Apply additional filtering based on the search_where parameter
        if where == "name":
            sstring = self.request.GET.get('search_string')
            queryset = queryset.filter(name__icontains=sstring)
        elif where == "landscape":
            queryset = queryset.filter(landscape=True)
        elif where == "main_colour":
            COLOUR_CHOICES_to_filter = ["Black", "Dark Blue", "Green", "Grey", "Light Blue", "Orange", "Pink", "Purple", "Red", "White", "Yellow"]
            queryset = queryset.filter(main_colour__in=COLOUR_CHOICES_to_filter)
        elif where == "artist":
            fotografi_group = Group.objects.get(name='Fotografi')
            queryset = queryset.filter(artist__in=User.objects.filter(groups__in=[fotografi_group]))

        return queryset

# views.py
class CreateFotoView(LoginRequiredMixin, CreateView):
    model = Foto
    fields = ['name', 'main_colour', 'landscape', 'price', 'actual_photo']
    template_name = 'APPfotoTempl/create_entry.html'
    success_url = reverse_lazy("APPfoto:home")

    def form_valid(self, form):
        form.instance.artist = self.request.user
        return super().form_valid(form)


@login_required
def my_situation(request):
     user = get_object_or_404(User, pk=request.user.pk)
     return render(request, "APPfotoTempl/situation.html")



@login_required
def CreaAcquisto(request, foto_id):
    foto = Foto.objects.get(pk=foto_id)

    if request.method == "POST":
        form = AcquistoForm(request.POST, initial={'foto': foto, 'acquirente': request.user})

        if form.is_valid():
            acquisto = form.save(commit=False)
            acquisto.foto = foto
            acquisto.acquirente = request.user
            acquisto.save()
            return redirect('APPfoto:situation')
        else:
            messages.error(request, "Invalid form data. Please correct the errors.")
    else:
        initial_data = {'foto': foto, 'acquirente': request.user}
        form = AcquistoForm(initial=initial_data)

    # Make the acquirente field readonly and disabled
    form.fields['acquirente'].widget.attrs['readonly'] = True
    form.fields['acquirente'].widget.attrs['disabled'] = True

    context = {
        'foto': foto,
        'form': form,
    }

    return render(request, 'APPfotoTempl/acquisto.html', context)


@login_required
def CreaRecensione(request, acquisto_id):
    acquisto = Acquisto.objects.get(pk=acquisto_id)
    foto = acquisto.foto

    existing_recensione = Recensione.objects.filter(utente=request.user, foto=foto).first()


    if request.method == "POST":
        form = RecensioneForm(request.POST, initial={'foto': foto, 'utente': request.user, 'fotografo': foto.artist})

        if form.is_valid():
            recensione = form.save(commit=False)
            recensione.foto = foto
            recensione.utente = request.user
            recensione.fotografo = foto.artist
            if existing_recensione:
                return redirect('APPfoto:situation')
            recensione.save()
            return redirect('APPfoto:situation')
        else:
            messages.error(request, "Invalid form data. Please correct the errors.")
    else:
        initial_data = {'foto': foto, 'utente': request.user, 'fotografo': foto.artist}
        form = RecensioneForm(initial=initial_data)

    # Make the acquirente field readonly and disabled
    form.fields['utente'].widget.attrs['readonly'] = True
    form.fields['utente'].widget.attrs['disabled'] = True
    form.fields['foto'].widget.attrs['readonly'] = True
    form.fields['foto'].widget.attrs['disabled'] = True
    form.fields['fotografo'].widget.attrs['readonly'] = True
    form.fields['fotografo'].widget.attrs['disabled'] = True

    context = {
        'foto': foto,
        'form': form,
        'user_has_recensione': existing_recensione is not None,
    }

    return render(request, 'APPfotoTempl/recensione.html', context)


@login_required
def RecensioniUtente(request):
    user = request.user
    recensioni_utente = Recensione.objects.filter(utente=user)

    context = {
        'user': user,
        'recensioni_utente': recensioni_utente,

    }

    return render(request, 'APPfotoTempl/recensioni_utente.html', context)
