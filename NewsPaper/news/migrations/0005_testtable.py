# Generated by Django 3.2.9 on 2021-12-08 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_rename_text2_post_text3'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testtable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Tetxxx', models.SmallIntegerField(default=0)),
            ],
        ),
    ]