# Generated by Django 4.0.2 on 2022-02-08 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('bio', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('bio', models.TextField(blank=True)),
                ('img', models.ImageField(blank=True, upload_to='profiles/')),
                ('is_active', models.BooleanField(default=True)),
                ('permissions', models.ManyToManyField(to='main.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.IntegerField()),
                ('bio', models.TextField(blank=True)),
                ('permission', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='main.permission')),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now=True)),
                ('lock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.lock')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.profile')),
            ],
        ),
    ]
