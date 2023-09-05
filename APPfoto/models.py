from django.db import models
from django.contrib.auth.models import User  # Import the User model from Django's built-in auth

class Foto(models.Model):
    COLOUR_CHOICES = [
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

    name = models.CharField(max_length=50, default="No name Given")
    main_colour = models.CharField(max_length=100, choices=COLOUR_CHOICES)
    landscape = models.BooleanField()
    actual_photo = models.ImageField(upload_to='APPfoto/static')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    price = models.DecimalField(verbose_name="prezzo", max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        if self.landscape:
            return f"Nome foto: {self.name}, scattata da: {self.artist}, colore principale: {self.main_colour}, ed è una foto landscape."
        else:
            return f"Nome foto: {self.name}, scattata da: {self.artist}, colore principale: {self.main_colour}, ed è una foto portrait."


class Recensione(models.Model):
    foto = models.ForeignKey(Foto, on_delete=models.CASCADE, related_name="recensioni")
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recensioni_scritte")
    testo = models.CharField(max_length=250, default="Questo utente non ha lasciato una recensione scritta, "
                                                     "solo un voto.")
    voto_positivo = models.BooleanField()
    fotografo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recensioni", null=True, blank=True)

    def scritta_da(self):
        return self.utente.username

    def testo_della_recensione(self):
        return self.testo

    def valutata(self):
        if self.voto_positivo:
            return "Valutata positivamente"
        else:
            return "Valutata negativamente"

    def save(self, *args, **kwargs):
        if self.foto:
            self.fotografo = self.foto.artist
        super(Recensione, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Recensioni"


class Acquisto(models.Model):
    MATERIALE_DI_STAMPA = [
        ("Carta Fotografica", "Carta Fotografica"),
        ("Tela", "Tela"),
        ("Carta Standard", "Carta Standard"),
        ("Lamiera Semplice", "Lamiera Semplice"),
        ("Lamiera Premium", "Lamiera Premium"),
        ("Puzzle", "Puzzle")
        ]

    DIMENSIONI = [
        ("10 x 15", "10 x 15"),
        ("12 x 18", "12 x 18"),
        ("13 x 19", "13 x 19")
    ]

    foto = models.ForeignKey(Foto, on_delete=models.CASCADE, related_name="venduti")
    acquirente = models.ForeignKey(User,on_delete=models.CASCADE, related_name="acquisti")
    materiale = models.CharField(max_length=100, choices=MATERIALE_DI_STAMPA)
    dimensioni = models.CharField(max_length=100, choices=DIMENSIONI)
