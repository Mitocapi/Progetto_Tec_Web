from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Foto, Acquisto


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
