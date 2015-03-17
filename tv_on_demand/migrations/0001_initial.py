# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mediafiles', '0001_initial'),
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=45, verbose_name='title')),
                ('slug', models.SlugField(max_length=45, editable=False)),
            ],
            options={
                'verbose_name': 'skin',
                'verbose_name_plural': 'skins',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('password', models.PositiveSmallIntegerField(null=True, verbose_name='password', blank=True)),
                ('chain', models.ForeignKey(verbose_name='chain', blank=True, to='clients.Chain', null=True)),
                ('mediadatabase', models.ForeignKey(verbose_name='media database', to='mediafiles.MediaDatabase')),
                ('skin', models.ForeignKey(verbose_name='skin', to='tv_on_demand.Skin')),
                ('store', models.ForeignKey(verbose_name='store', blank=True, to='clients.Store', null=True)),
            ],
            options={
                'verbose_name': 'structure',
                'verbose_name_plural': 'structures',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StructureRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('label', models.TextField(null=True, verbose_name='description', blank=True)),
                ('order', models.PositiveIntegerField(verbose_name='order')),
                ('mediafile', models.ForeignKey(verbose_name='media', blank=True, to='mediafiles.MediaFile', null=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='tv_on_demand.StructureRow', null=True)),
                ('structure', models.ForeignKey(verbose_name='structure', to='tv_on_demand.Structure')),
            ],
            options={
                'verbose_name': 'row',
                'verbose_name_plural': 'rows',
            },
            bases=(models.Model,),
        ),
    ]
