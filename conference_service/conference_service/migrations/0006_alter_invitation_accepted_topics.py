# Generated by Django 4.2.7 on 2023-12-02 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conference_service', '0005_invitation_accepted_topics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='accepted_topics',
            field=models.TextField(blank=True),
        ),
    ]
