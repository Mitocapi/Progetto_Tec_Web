# Generated by Django 4.2.4 on 2023-09-06 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APPfoto', '0008_foto_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foto',
            name='actual_photo',
            field=models.ImageField(upload_to='uploads/'),
        ),
    ]
