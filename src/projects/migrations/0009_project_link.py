# Generated by Django 2.1.7 on 2019-04-20 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_auto_20190413_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='link',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]