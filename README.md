# foto_commerce3
librerie utilizzate nella realizzazione del progetto: 
- crispy-forms e django-bootstrap4 sono stati utilizzati per migliorare l'aspetto grafico
del sito e la User experience, per poterli usare è necessario installarli tramite
pip e inserirli nella sezione installed_apps del file settings.py messo a disposizione
da django dopodichè è sufficiente aggiungere Helper al form e caricare nel template
attraverso l'apposito comando {% load crispy_forms_tags %} le funzioni di crispy form
e bootstrap

-django-extensions è stato utilizzato per creare un primo class diagram generale del
per poterlo usare è stato anche in questo caso necessario installarlo tramite pip e
inserirlo in installed_apps, dopodichè è stato necessario installare, sempre per mezzo
di pip, graphviz che ci permette di realizzare il grafico
