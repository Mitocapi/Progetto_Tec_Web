from django.shortcuts import redirect, get_object_or_404
from .forms import *
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from decimal import Decimal, ROUND_UP
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import SearchForm
from django.shortcuts import render
from django.views import View
from django.db.models import Avg, F, ExpressionWrapper, fields, Count


def home_view(request):
    return render(request, template_name="APPfotoTempl/home.html")



class FotografiListView(ListView):
    template_name = 'APPfotoTempl/lista_fotografi.html'
    context_object_name = 'members'

    def get_queryset(self):
        fotografi_group = Group.objects.get(name='Fotografi')
        members = User.objects.filter(groups=fotografi_group).annotate(
            average_review=ExpressionWrapper(
                Avg(F('recensioni__voto')),
                output_field=fields.FloatField()
            )
        ).annotate(
            foto_count=Count('foto')
        )

        # Check the 'sort' query parameter and apply sorting
        sort_by = self.request.GET.get('sort')
        if sort_by == 'positive_reviews':
            members = members.order_by('-average_review')
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
            queryset = queryset.order_by('-creation_date')

        return queryset


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_where = form.cleaned_data['search_where']

            if search_where == "name":
                sstring = form.cleaned_data['search_string']
            elif search_where == "landscape":
                sstring = form.cleaned_data['landscape']
            elif search_where == "main_colour":
                sstring = form.cleaned_data['main_colour']
            elif search_where == "artist":
                sstring = form.cleaned_data['artist']


            if not sstring:
                sstring = "SEARCH SOMETHING, ANYTHING"

            return redirect("APPfoto:ricerca_risultati", sstring=sstring, where=search_where)

    else:
        form = SearchForm()
    return render(request, 'APPfotoTempl/search.html', {'form': form})


class FotoListaRicercataView(FotoListView):
    titolo = "risultati ricerca"

    def get_queryset(self):
        queryset = super().get_queryset()
        where = self.kwargs['where']
        sstring = self.kwargs['sstring']


        sort = self.request.GET.get('sort')
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == 'new':
            queryset = queryset.order_by('-creation_date')


        if where == "name":
            queryset = queryset.filter(name__icontains=sstring)
        elif where == "landscape":
            if sstring=="True":
                queryset = queryset.filter(landscape=True)
            else:
                queryset = queryset.filter(landscape=False)
        elif where == "main_colour":
            sstring = self.kwargs['sstring']
            queryset = queryset.filter(main_colour__icontains=sstring)

        elif where == "artist":
            queryset = queryset.filter(artist=sstring)

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

            materiale_value = float(form.cleaned_data['materiale'])
            dimensioni_value = float(form.cleaned_data['dimensioni'])

            foto_price = float(foto.price)

            prezzo = Decimal(foto_price) + Decimal(materiale_value) + Decimal(dimensioni_value)
            prezzo = prezzo.quantize(Decimal('0.00'), rounding=ROUND_UP)

            acquisto.prezzo = prezzo

            acquisto.save()
            return redirect('APPfoto:situation')
        else:
            messages.error(request, "Invalid form data. Please correct the errors.")
    else:
        initial_data = {'foto': foto, 'acquirente': request.user}
        form = AcquistoForm(initial=initial_data)


    form.fields['acquirente'].widget.attrs['readonly'] = True
    form.fields['acquirente'].widget.attrs['disabled'] = True

    form.fields['materiale'].label = "Materiale"
    form.fields['dimensioni'].label = "Dimensioni"

    context = {
        'foto': foto,
        'form': form,
    }

    return render(request, 'APPfotoTempl/acquisto.html', context)


@login_required
def CreaRecensione(request, acquisto_id):
    acquisto = get_object_or_404(Acquisto, pk=acquisto_id)
    existing_recensione = Recensione.objects.filter(acquisto=acquisto, utente=request.user).first()
    foto = get_object_or_404(Foto, pk=acquisto.foto_id)

    print(acquisto)


    if request.method == 'POST':
        form = RecensioneForm(request.POST, initial={'foto': foto, 'acquisto': acquisto, 'utente': request.user,
                                                     'fotografo' : foto.artist})
        if form.is_valid():
            recensione = form.save(commit=False)
            recensione.acquisto = acquisto
            recensione.utente = request.user
            recensione.foto = foto
            recensione.fotografo = foto.artist
            recensione.save()
            return redirect('APPfoto:situation')
        else:
            messages.error(request, "Form non valido, sistemare per favore")
    else:
        initial_data = {'foto': foto, 'acquisto': acquisto, 'utente': request.user,
                   'fotografo': foto.artist}
        form = RecensioneForm(initial=initial_data)

    form.fields['utente'].widget.attrs['readonly'] = True
    form.fields['utente'].widget.attrs['disabled'] = True
    form.fields['foto'].widget.attrs['readonly'] = True
    form.fields['foto'].widget.attrs['disabled'] = True

    context = {
        'acquisto': acquisto_id,
        'foto': acquisto.foto_id,
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
