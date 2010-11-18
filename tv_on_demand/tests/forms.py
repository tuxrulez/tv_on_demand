#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from mediafiles.models import MediaFile
from tv_on_demand.forms import StructureForm, StructureRowForm
from tv_on_demand.models import Structure, Skin

FILEPATH = os.path.abspath(os.path.dirname(__file__))

class StructureFormTest(TestCase):    
   
    fixtures = ['skins.json']
   
    def create_user(self, username='admin'):
        email = '%s@somedomain.com' %username
        return User.objects.create_user(username=username, email=email, password='123')
        
    def get_data(self):
        skin = Skin.objects.all()[0]
        data = {'name': 'test', 'users': [self.create_user().pk],
                'date_start': '14/05/1989 14:15', 'date_end': '21/12/2098 18:22',
                'skin': skin.pk}
        return data    
   
     
    def test_valid_data(self):
        form = StructureForm(self.get_data())        
        
        self.assertTrue(form.is_valid())        
        
        
class StructureRowFormTest(TestCase):
    
    fixtures = ['structures.json', 'mediafiles.json']
    
    def setUp(self):
        structure = Structure.objects.all()[0]
        
        self.default_data = {'structure': structure.pk, 'label': 'test label', 'title': 'test title',
                            'date_start': '14/05/1989 14:15', 'date_end': '21/12/2098 21:10', 'order': 0,
                            'entry': 'latest'}

        
    def test_row(self):
        form = StructureRowForm(self.default_data)        
        
        self.assertTrue(form.is_valid())

    
    def test_without_row_content(self):
        invalid_data = self.default_data
        invalid_data['entry'] = None
        form = StructureRowForm(invalid_data)

        self.assertFalse(form.is_valid())
        
    
    def test_multiple_row_content(self):
        mediafile = MediaFile.objects.all()[0]
        invalid_data = self.default_data
        invalid_data['mediafile'] = mediafile.pk
        form = StructureRowForm(invalid_data)
        
        self.assertFalse(form.is_valid())
        
        
        
        
        
        
        
        
