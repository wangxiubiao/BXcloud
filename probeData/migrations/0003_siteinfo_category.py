# Generated by Django 2.0.13 on 2019-07-26 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('probeData', '0002_auto_20190724_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteinfo',
            name='category',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
