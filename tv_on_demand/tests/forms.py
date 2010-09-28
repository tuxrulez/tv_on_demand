#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from tv_on_demand.forms import StructureForm

FILEPATH = os.path.abspath(os.path.dirname(__file__))

class StructureFormTest(TestCase):    
   
    def create_user(self, username='admin'):
        email = '%s@somedomain.com' %username
        return User.objects.create_user(username=username, email=email, password='123')
        
    def get_data(self):
        data = {'name': 'test', 'users': [self.create_user().pk],
                'date_start': '14/05/1989 14:15', 'date_end': '21/12/2098 18:22'}
        return data
    
    def template_data(self, filename='sample.swf'):
        template = open(os.path.join(FILEPATH, 'files', filename), 'rb')
        return {'template': SimpleUploadedFile(template.name, template.read())}        
     
    def test_valid_data(self):
        form = StructureForm(self.get_data(), self.template_data())        
        
        self.assertTrue(form.is_valid())
        
    def test_invalid_template(self):
        form = StructureForm(self.get_data(), self.template_data('sample.jpg'))
        
        self.assertFalse(form.is_valid())
    
