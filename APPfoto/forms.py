from .models import *
from django.contrib.auth.models import User,Group
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class SearchForm(forms.Form):
    CHOICE_LIST = [
        ("name", "Cerca nome foto"),
        ("artist", "Cerca nome fotografo"),
        ("main_colour", "Cerca per colore principale"),
        ("landscape", "Cerca per orientamento"),
    ]

    COLOUR_CHOICES = [
        ("", "Select Color"),
        ("Black", "Black"),
        ("Dark Blue", "Dark Blue"),
        ("Green", "Green"),
        ("Grey", "Grey"),
        ("Light Blue", "Light Blue"),
        ("Orange", "Orange"),
        ("Pink", "Pink"),
        ("Purple", "Purple"),
        ("Red", "Red"),
        ("White", "White"),
        ("Yellow", "Yellow"),
    ]

    fotografi_group = Group.objects.get(name='Fotografi')
    users_in_groups = User.objects.filter(groups__in=[fotografi_group])


    artist_choices = [("", "Select Fotografo")] + [(user.id, user.username) for user in users_in_groups]
    helper = FormHelper()
    helper.form_id = 'search_crispy_form'
    helper.form_method = "POST"
    helper.add_input(Submit('submit', 'Cerca'))

    search_where = forms.ChoiceField(label="Criterio di ricerca: ", required=True, choices=CHOICE_LIST)
    search_string = forms.CharField(label="Nome foto", max_length=100, min_length=1, required=False)
    artist = forms.ChoiceField(label="Fotografo", required=False, choices=artist_choices)
    main_colour = forms.ChoiceField(label="Colore principale", required=False, choices=COLOUR_CHOICES)
    landscape = forms.BooleanField(label="Formato landscape", required=False)


class CreateFotoForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "addfoto_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Aggiungi Foto"))


    class Meta:
        model = Foto
        fields = ["name", "main_colour", "price", "landscape", "actual_photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["artist"].widget.attrs["readonly"] = True


class AcquistoForm(forms.ModelForm):
    class Meta:
        model = Acquisto
        fields = ["foto", "acquirente", "materiale", "dimensioni"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["acquirente"].disabled = True
        self.fields["foto"].disabled = True

        self.helper = FormHelper()
        self.helper.form_id = "acquisto_crispy_form"
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Completa l'acquisto"))



class RecensioneForm(forms.ModelForm):
    class Meta:
        model = Recensione
        fields = ['acquisto', 'foto', 'fotografo', 'utente', 'voto', 'testo']

    voto = forms.IntegerField(min_value=0, max_value=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["acquisto"].disabled = True
        self.fields["foto"].disabled = True
        self.fields["utente"].disabled = True
        self.fields["fotografo"].disabled = True


        # Helper per crispy
        self.helper = FormHelper()
        self.helper.form_id = "recensione_crispy_form"
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Conferma la recensione"))

