#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from mediafiles.models import MediaFile
from tv_on_demand.models import Structure

FILEPATH = os.path.abspath(os.path.dirname(__file__))

class StructureViewTest(TestCase):
    
    fixtures = ['structures.json']
    userdata = {'username': 'admin', 'password': 'admin123',
                'email': 'admin@admin.com'}
                
    def setUp(self):
        self.user = User.objects.create_user(**self.userdata)
        # INTRIGANTE: Permission já vem carregado mesmo sem fixtures o_O
        add_structure_perm = Permission.objects.get(codename='add_structure')
        change_structure_perm = Permission.objects.get(codename='change_structure')
        add_row_perm = Permission.objects.get(codename='add_structurerow')
        change_row_perm = Permission.objects.get(codename='change_structurerow')
        self.user.user_permissions.add(add_structure_perm, change_structure_perm,
                                       add_row_perm, change_row_perm)
        
        self.client.login(username=self.userdata['username'], password=self.userdata['password'])        
    
    def test_add(self):
        url = reverse('admin:tv_on_demand_structure_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tv_on_demand/structure_form.html')
        
    def test_ajax_add(self):
        url = reverse('tod_structure_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        
    def test_wrong_ajax_add(self):
        url = reverse('tod_structure_ajax_add')
        data = {}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
        
    def test_save(self):
        url = reverse('tod_structure_ajax_add')
        tmpl = open(os.path.join(FILEPATH, 'files', 'sample.swf'), 'rb')
        data = {'name': 'test melancia', 'template': tmpl}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertTrue(Structure.objects.filter(name=data['name']))
        self.assertContains(response, data['name'])
        self.assertContains(response, data['template'].name.split('.')[-1])
        self.assertContains(response, 'id')
        
    def test_save_errors(self):
        url = reverse('tod_structure_ajax_add')
        data = {'name': 'test abacaxi'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertFalse(Structure.objects.filter(name=data['name']))
        self.assertContains(response, 'errors')
        
    def test_ajax_change(self):
        structure = Structure.objects.all()[0]
        url = reverse('tod_structure_ajax_change', args=[structure.pk])
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        
    def test_wrong_ajax_change(self):
        structure = Structure.objects.all()[0]
        url = reverse('tod_structure_ajax_change', args=[structure.pk])
        data = {}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
        
    def test_wrong_id_ajax_change(self):
        url = reverse('tod_structure_ajax_change', args=[666])
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
        
    def test_save_change(self):
        instance = Structure.objects.create(name='test structure', template='tpl.swf')
        url = reverse('tod_structure_ajax_change', args=[instance.pk])
        data = {'name': 'new structure name'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        new_instance = Structure.objects.get(pk=instance.pk)
        self.assertEqual(data['name'], new_instance.name)
        self.assertEqual(instance.template, new_instance.template)
        
        
class StructureNoPermissions(TestCase):
    
    fixtures = ['structures.json']
    
    def test_add(self):
        url = reverse('admin:tv_on_demand_structure_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        
    def test_ajax_add(self):
        url = reverse('tod_structure_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        
    def test_ajax_change(self):
        structure = Structure.objects.all()[0]
        url = reverse('tod_structure_ajax_change', args=[structure.pk])
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        
 

class StructureRowViewTest(TestCase):
    
    fixtures = ['structures.json', 'mediafiles.json']    
    userdata = {'username': 'admin', 'password': '123', 'email': 'admin@admin.com'}
    
    def setUp(self):
        self.user = User.objects.create_user(**self.userdata)
        add_perm = Permission.objects.get(codename='add_structurerow')
        self.user.user_permissions.add(add_perm)
        self.client.login(username=self.userdata['username'], password=self.userdata['password'])
        
        structure = Structure.objects.all()[0]
        mediafile = MediaFile.objects.all()[0]
        
        self.default_data = {'structure': structure, 'title': 'test title', 'label': 'test label',
                             'mediafile': mediafile, 'date_start': '14/05/1989 14:15',
                             'date_end': '21/12/2098 21:10', 'order': 0, 'users': [self.user.pk]}    
    
    def test_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        
        
    def test_wrong_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = {}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
        
        
    def test_ajax_add_save(self):
        url = reverse('tod_structurerow_ajax_add')
        data = {}
        


class StructureRowNoPermissions(TestCase):
    
    def test_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
        
        
        
        
        
        
        
        

        
    
        