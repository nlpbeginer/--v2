# Generated by Django 4.2.7 on 2023-12-02 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paper_service', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='decision',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(blank=True),
        ),
    ]