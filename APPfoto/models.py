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
    actual_photo = models.ImageField(upload_to='uploads/')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    price = models.DecimalField(verbose_name="prezzo", max_digits=5, decimal_places=2, default=0.00)
    creation_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.landscape:
            return f"Nome foto: {self.name}, in formato landscape"
        else:
            return f"Nome foto: {self.name}, in formato portrait."




class Acquisto(models.Model):

    MATERIALE_DI_STAMPA = [
        ("0.00", "Carta Standard (+0.00)"),
        ("1.00", "Tela (+1.00)"),
        ("2.00", "Carta Fotografica (+2.00)"),
        ("3.50", "Puzzle (+3.50)"),
        ("3.00", "Lamiera Semplice (+3.00)"),
        ("4.00", "Lamiera Premium (+4.00)")
    ]

    DIMENSIONI = [
        ("0.00", "10 x 15   (+0.00)"),
        ("2.00", "12 x 18   (+2.00)"),
        ("3.00", "13 x 19   (+3.00)")
    ]

    foto = models.ForeignKey(Foto, on_delete=models.CASCADE, related_name="venduti")
    acquirente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acquisti")
    materiale = models.CharField(max_length=100, choices=MATERIALE_DI_STAMPA)
    dimensioni = models.CharField(max_length=100, choices=DIMENSIONI)
    prezzo = models.DecimalField(verbose_name="prezzo", max_digits=6, decimal_places=2, blank=True, null=True)


class Recensione(models.Model):
    foto = models.ForeignKey(Foto, on_delete=models.CASCADE, related_name="recensioni")
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recensioni_scritte")
    testo = models.CharField(max_length=250, default="Questo utente non ha lasciato una recensione scritta, "
                                                     "solo un voto.")
    voto = models.PositiveIntegerField()
    fotografo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recensioni", null=True, blank=True)
    acquisto=models.ForeignKey(Acquisto, on_delete=models.CASCADE, related_name="recensioni", null=True, blank=True)

    def scritta_da(self):
        return self.utente.username

    def testo_della_recensione(self):
        return self.testo

    def valutata(self):
       return "Valutata " + str(self.voto) + " su 10"

    def save(self, *args, **kwargs):
        if self.foto:
            self.fotografo = self.foto.artist
        super(Recensione, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Recensioni"
