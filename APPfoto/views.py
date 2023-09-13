from django.db.models.functions import Coalesce
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
from django.db.models import Avg, Count, Subquery, OuterRef, Value


def home_view(request):
    return render(request, template_name="APPfotoTempl/home.html")


def forYouView(request):
    user = request.user

    # PRIMO PASSO: fotografo preferito dall'utente
    if user.is_authenticated:
        fotografo_prefe = Recensione.objects.filter(
            acquisto__acquirente=user
        ).values('acquisto__foto__artist').annotate(
            avg_rating=Avg('voto')
        ).order_by('-avg_rating').first()
    else:
        fotografo_prefe = None

    # SECONDO PASSO, le foto del fotografo prefe o del miglior fotografo complessivamente
    if fotografo_prefe:
        preferenze = Foto.objects.filter(artist=fotografo_prefe['acquisto__foto__artist'])[:7]
    else:
        best_photographer = Recensione.objects.values('acquisto__foto__artist').annotate(
            avg_rating=Avg('voto')
        ).order_by('-avg_rating').first()

        if best_photographer:
            preferenze = Foto.objects.filter(artist=best_photographer['acquisto__foto__artist'])[:7]
        else:
            preferenze = []

    foto_recenti = Foto.objects.order_by('-creation_date')[:7]

    best_selling_foto = Foto.objects.annotate(
        acquisto_count=Count('venduti')
    ).order_by('-acquisto_count')[:7]

    context = {
        'foto_recenti': foto_recenti,
        'best_selling_foto': best_selling_foto,
        'le_tue_preferenze': preferenze,
    }

    return render(request, 'APPfotoTempl/for_you_page.html', context)

class FotografiListView(ListView):
    template_name = 'APPfotoTempl/lista_fotografi.html'
    context_object_name = 'members'

    def get_queryset(self):
        fotografi_group = Group.objects.get(name='Fotografi')

        subquery = Acquisto.objects.filter(foto__artist=OuterRef('pk')).values('foto__artist').annotate(
            venduti_count=Count('id')
        ).values('venduti_count')

        members = User.objects.filter(groups=fotografi_group).annotate(
            average_review=Avg('recensioni__voto'),
            foto_count=Count('foto', distinct=True),  # Count distinct photos
            venduti_count=Subquery(subquery[:1])
        )

        sort_by = self.request.GET.get('sort')
        if sort_by == 'positive_reviews':
            members = members.order_by('-average_review')
        elif sort_by == 'alphabetical':
            members = members.order_by('username')
        elif sort_by == 'best_seller':
            members = members.order_by('-venduti_count')

        return members



class FotoListView(ListView):
    titolo = "Abbiamo trovato queste foto"
    model = Foto
    template_name = "APPfotoTempl/lista_foto.html"


    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort', None)

        queryset = queryset.annotate(
            acquisto_count=Coalesce(Count('venduti'), Value(0, output_field=models.IntegerField())))

        queryset = queryset.order_by('-creation_date')

        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == 'new':
            queryset = queryset.order_by('-creation_date')
        elif sort == 'best seller':
            queryset = queryset.order_by('-acquisto_count')

        return queryset


class FotoListaRicercataView(FotoListView):
    model = Foto
    template_name = "APPfotoTempl/lista_foto.html"
    titolo = 'risultati ricerca'

    def get_queryset(self):
        where = self.kwargs['where']
        sstring = self.kwargs['sstring']

        queryset = Foto.objects.all()

        queryset = queryset.annotate(
            acquisto_count=Coalesce(Count('venduti'), Value(0, output_field=models.IntegerField())))

        if where == "name":
            queryset = queryset.filter(name__icontains=sstring)
        elif where == "landscape":
            if sstring == "True":
                queryset = queryset.filter(landscape=True)
            else:
                queryset = queryset.filter(landscape=False)
        elif where == "main_colour":
            queryset = queryset.filter(main_colour__icontains=sstring)
        elif where == "artist":

            queryset = queryset.filter(artist__id=sstring)

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
    artist = foto.artist

    # LISTONE DELLE FOTO DI STO TIZIO MA TOLGO LA FOTO CORRENTR
    artist_photos = Foto.objects.filter(artist=artist).exclude(pk=foto_id)

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
        'artist_photos': artist_photos
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
