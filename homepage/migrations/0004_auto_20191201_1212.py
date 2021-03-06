# Generated by Django 2.2.5 on 2019-12-01 06:42

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('homepage', '0003_auto_20191122_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='date_of_post',
            field=models.DateField(default=datetime.date(2019, 12, 1)),
        ),
        migrations.CreateModel(
            name='review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=150, null=True)),
                ('rating', models.IntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
