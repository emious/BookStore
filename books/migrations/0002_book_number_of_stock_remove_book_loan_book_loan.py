# Generated by Django 4.1 on 2022-09-08 13:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='number_of_stock',
            field=models.IntegerField(default=0),
        ),
        migrations.RemoveField(
            model_name='book',
            name='loan',
        ),
        migrations.AddField(
            model_name='book',
            name='loan',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]