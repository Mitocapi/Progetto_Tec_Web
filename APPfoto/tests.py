from django.test import TestCase
from .models import Acquisto,Foto,Recensione
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse


class FotoListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crea i Fotografi
        group_name = "Fotografi"
        cls.group = Group.objects.create(name=group_name)

    def setUp(self):

        user = User.objects.create_user(username="user", password="password")

        fotografi_group, created = Group.objects.get_or_create(name='Fotografi')
        fotoguser = User.objects.create_user(username='testuser', password='password')
        fotoguser.groups.add(fotografi_group)
        fotoguser2 = User.objects.create_user(username='testuser2', password='password')
        fotoguser2.groups.add(fotografi_group)

        # crwa delle foto
        foto1 = Foto.objects.create(name="Foto 1", venduti=3, price=10, artist=fotoguser )
        foto2 = Foto.objects.create(name="Foto 2", venduti=5, price=15, artist=fotoguser )
        foto3 = Foto.objects.create(name="Foto 3", venduti=0, price=20, artist= fotoguser2 )

        #creo acquisti
        self.acquisto1 = Acquisto.objects.create(foto=foto1, acquirente=user)
        self.acquisto2 = Acquisto.objects.create(foto=foto1, acquirente=user)
        self.acquisto3 = Acquisto.objects.create(foto=foto2, acquirente=user)

    def test_view_returns_200(self):
        response = self.client.get(reverse('APPfoto:listafoto'))
        self.assertEqual(response.status_code, 200)

    def test_view_mostra_foto_con_acquisto_count(self):
        response = self.client.get(reverse('APPfoto:listafoto'))
        self.assertContains(response, 'Copie vendute: 3', count=1)
        self.assertContains(response, 'Copie vendute: 5', count=1)
        self.assertContains(response, 'Copie vendute: 0', count=1)

    def test_sort_by_best_seller(self):
        response = self.client.get(reverse('APPfoto:listafoto') + '?sort=best%20seller')

        # ordine di vendite...
        expected_sorted_fotos = Foto.objects.order_by('-acquisto_count')
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_sorted_fotos,
            transform=lambda x: x,
        )

    def test_sort_by_prezzo(self):
        response = self.client.get(reverse('your_foto_list_view_name') + '?sort=price')

        # Check if the response displays photos sorted by price in ascending order.
        expected_sorted_fotos = Foto.objects.order_by('price')
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_sorted_fotos,
            transform=lambda x: x,
        )

    def test_sort_by_new(self):
        response = self.client.get(reverse('APPfoto:listafoto') + '?sort=new')

        # Testiamo se ordnia by new
        expected_sorted_fotos = Foto.objects.order_by('-creation_date')
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_sorted_fotos,
            transform=lambda x: x,
        )

    def test_no_photos_available_message(self):
        Foto.objects.all().delete()
        response = self.client.get(reverse('APPfoto:listafoto'))
        self.assertContains(response, 'No photos available', count=1)
