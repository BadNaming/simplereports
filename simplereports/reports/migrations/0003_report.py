# Generated by Django 4.1.5 on 2023-06-10 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0002_temporarydata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок отчета')),
                ('status', models.CharField(choices=[('process', 'В процессе формирования'), ('ready', 'Сформирован'), ('error', 'Ошибка формирования')], default='process', max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата формирования отчета')),
                ('file_name', models.CharField(max_length=100, verbose_name='Название файла')),
                ('url', models.FilePathField(path='/home/alexandra/Dev/simplereports/simplereports/reports')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL, verbose_name='Автор отчета')),
            ],
        ),
    ]