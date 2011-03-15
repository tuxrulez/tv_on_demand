#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from model_mommy import mommy
from tv_on_demand.models import Structure, StructureRow, Skin
from mediafiles.models import MediaFile, MediaDatabase

#helpers
now = datetime.now()
later = datetime.now() + timedelta(days=10)

TESTPATH = os.path.abspath(os.path.dirname(__file__))

def create_user(username='nobody'):
    email = '%s@somedomain.com' %username
    return User.objects.create_user(username=username, password='123', email=email)


def create_structure(skin, name='test name', **kwargs):
    mediadatabase = mommy.make_one(MediaDatabase)

    data = {'name': name, 'skin': skin} 
    data.update(kwargs)
    
    return Structure.objects.create(**data)
    
def create_structurerow(skin, structure=None, title='test title', label='test label',\
                        date_start=now, date_end=later, entry='latest', order=0, **kwargs):
    
    if not structure:
        structure = create_structure(skin=skin)

    data = {'structure': structure, 'title': title, 'label': label, 'date_start': date_start,
            'date_end': date_end, 'entry': entry, 'order': order}
    data.update(**kwargs)
    
    instance = StructureRow.objects.create(**data)
    #instance.users.add(create_user())

    return instance


class StructureModelTest(TestCase):
    
    fixtures = ['skins.json']
    
    def setUp(self):
        self.skin = Skin.objects.all()[0]
    
    def test_creation(self):
        instance = create_structure(skin=self.skin)
        
        self.assertEqual(Structure.objects.count(), 1)
        
        
    def test_generic_relation(self):
        related_object = create_structure(self.skin)
        ctype = ContentType.objects.get_for_model(related_object)
        instance = create_structure(self.skin, content_type=ctype, object_id=related_object.pk)
        
        self.assertEqual(instance.content_object.pk, related_object.pk)
        

    def test_parmalink(self):
        instance = create_structure(self.skin)        
        self.assertTrue(instance.get_absolute_url())
        


class StructureRowModelTest(TestCase):
    
    fixtures = ['mediafiles.json', 'quizzes.json', 'skins.json']
    
    def setUp(self):
        self.skin = Skin.objects.all()[1]
    
    
    def test_creation(self):
        mediafile = MediaFile.objects.all()[0]
        instance = create_structurerow(self.skin, mediafile=mediafile)
        
        self.assertEqual(StructureRow.objects.count(), 1)


    def test_br_datetime(self):
        instance = create_structurerow(self.skin)
        date_start_output = instance.br_datetime('date_start')
        
        self.assertEqual(date_start_output, instance.date_start.strftime('%d/%m/%Y %H:%M'))
        
        
class SkinModelTest(TestCase):
    
    def test_creation(self):
        instance = Skin.objects.create(title='Test Skin')
        
        self.assertEqual(Skin.objects.count(), 1)
    
    
  
    
        
