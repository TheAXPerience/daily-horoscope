# Generated by Django 4.2.5 on 2023-09-07 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0002_alter_customuser_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(null=True),
        ),
    ]
