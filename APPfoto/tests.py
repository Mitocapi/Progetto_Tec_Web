from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User,Group
from .models import Foto, Acquisto
from .forms import SearchForm


class CreaAcquistoViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
    def test_crea_acquisto_valido_post(self):

        foto = Foto.objects.create(name='nomefoto',artist=self.user,price=10, actual_photo='fototest.jpg', landscape=True )

        form_data = {
            'materiale': '0.00',
            'dimensioni': '0.00',
        }

        response = self.client.post(reverse('APPfoto:acquisto', args=[foto.id]), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('APPfoto:situation'))
        self.assertTrue(Acquisto.objects.filter(foto=foto, acquirente=self.user).exists())

    def test_crea_acquisto_invalido_post(self):
        foto2 = Foto.objects.create(name='nomefoto2',artist=self.user,price=10, actual_photo='fototest2.jpg', landscape=True )

        form_data = {
            'dimensioni' : 99,
            'materiale' : 'legno'
        }

        response = self.client.post(reverse('APPfoto:acquisto', args=[foto2.id]), data=form_data)

        self.assertEqual(response.status_code, 200)



    def test_form_rendering(self):

        foto3 = Foto.objects.create(name='nomefoto3', artist=self.user, price=10, actual_photo='fototest3.jpg',
                                   landscape=True)

        response = self.client.get(reverse('APPfoto:acquisto', args=[foto3.id]))
        self.assertEqual(response.status_code, 200)

        #contiene quello che deve contenere

        self.assertTemplateUsed(response, 'APPfotoTempl/acquisto.html')
        self.assertContains(response, '<form', count=1)
        self.assertContains(response, 'id="id_materiale"', count=1)
        self.assertContains(response, 'id="id_dimensioni"', count=1)
        self.assertContains(response, 'id="id_foto"', count=1)


    def test_campi_form_prefatti_data(self):

        foto4 = Foto.objects.create(name='nomefoto4', artist=self.user, price=10, actual_photo='fototest4.jpg',
                                   landscape=True)

        response = self.client.get(reverse('APPfoto:acquisto', args=[foto4.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'APPfotoTempl/acquisto.html')

        #controllo che sia pieno il pieno e vuoto il votuo
        form = response.context['form']
        self.assertEqual(form.initial['foto'], foto4)
        self.assertEqual(form.initial['acquirente'], self.user)
        self.assertContains(response, 'id='"id_materiale", count=0)
        self.assertContains(response, 'id="dimensioni"', count=0)

    def test_user_not_logged_in(self):
        self.client = Client()
        foto5 = Foto.objects.create(name='nomefoto5', artist=self.user, price=10, actual_photo='fototest5.jpg',
                                   landscape=True)

        response = self.client.get(reverse('APPfoto:acquisto', args=[foto5.id]))

        self.assertEqual(response.status_code, 302)
        actual_url = response.url

        # viene rediretto all'url di login e poi torna alla foto
        self.assertEqual(actual_url, '/login/?auth=notok&next=/APPfoto/acquisto/1/')



class SearchFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='fotografi_user', password='testpassword')
        fotografi_group, created = Group.objects.get_or_create(name='Fotografi')
        self.user.groups.add(fotografi_group)

    def test_search_form_rendering(self):
        client = Client()
        response = self.client.get(reverse('APPfoto:cercaFoto'))  # Replace with your actual URL
        self.assertContains(response, '<form', count=1)
        self.assertContains(response, 'id="id_search_where"', count=1)
        self.assertContains(response, 'id="id_search_string"', count=1)
        self.assertContains(response, 'id="id_artist"', count=1)
        self.assertContains(response, 'id="id_main_colour"', count=1)
        self.assertContains(response, 'id="id_landscape"', count=1)

    def test_search_form_non_valido(self):
        form_data = {
            'search_where':99,
            'search_string' : 'NON BOOLEAN'
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)

        form_data = {
            'search_where': "",
            'search_string': 'NON BOOLEAN'
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)

        form_data = {
            'search_where': "not a field",
            'search_string': 9
        }

        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)

        form_data = {
            'search_where': None,
            'search_string': 'NON BOOLEAN'
        }

        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)

        form_data = {
            'search_where': "artist",
            'search_string': None,
            'artist': 99
        }

        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)


        form_data = {
            'search_where': "main_colour",
            'main_colour': "non choice ma still str"
        }

        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)

        form_data = {
            'search_where': "main_colour",
            'main_colour': 99
        }

        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors), 1)



    def test_search_form_choices(self):
        form = SearchForm()
        artist_field = form.fields['artist']
        self.assertGreaterEqual(len(artist_field.choices), 1)

        form = SearchForm()
        main_colour_field = form.fields['main_colour']
        self.assertGreaterEqual(len(main_colour_field.choices), 1)

    def test_valid_search_form(self):
        form_data = {
            'search_where': 'name',
            'search_string': 'Test Photo',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'search_where': 'landscape',
            'search_string': 'not a boolean',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'search_where': 'landscape',
            'search_string': True,
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'search_where': 'artist',
            'search_string': 'string',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'search_where': 'main_colour',
            'search_string': 'Orange',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'search_where': 'main_colour',
            'search_string': 'not a colour but still a string',
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class MySituationViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')


    def test_authenticated_user_can_access(self):

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('APPfoto:situation'))

        # 200=ok
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_is_redirected(self):
        # entra in situation senza essere loggato
        response = self.client.get(reverse('APPfoto:situation'))

        self.assertEqual(response.status_code, 302)
        actual_url = response.url

        # viene rediretto all'url di login e poi torna alla pagina
        self.assertEqual(actual_url, '/login/?auth=notok&next=/APPfoto/situation/')

    def test_correct_template_used(self):

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('APPfoto:situation'))

        # controlla il templ
        self.assertTemplateUsed(response, 'APPfotoTempl/situation.html')

    def test_purchase_history_displayed(self):
        self.client.login(username='testuser', password='testpassword')

        self.foto = Foto.objects.create(
            name='Test Photo',
            main_colour='Blue',
            landscape=True,
            price=20.0,
            actual_photo='test.jpg',
            artist=self.user
        )

        acquisto = Acquisto.objects.create(
            foto=self.foto,
            acquirente=self.user,
            prezzo=20.0,
            materiale="0.00",
            dimensioni="0.00"
        )

        response = self.client.get(reverse('APPfoto:situation'))
        self.assertContains(response, 'Ecco l\'elenco dei tuoi acquisti')

        # We gucci url?
        self.assertContains(response, 'card-title')
        self.assertContains(response, 'card-text')
        self.assertContains(response, 'Scrivi una Recensione')
        self.assertContains(response, 'Spesa totale: ')