#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from tv_on_demand.models import Structure

FILEPATH = os.path.abspath(os.path.dirname(__file__))

class StructureViewTest(TestCase):
    
    userdata = {'username': 'admin', 'password': 'admin123',
                'email': 'admin@admin.com'}
                
    def setUp(self):
        self.user = User.objects.create_user(**self.userdata)
        # INTRIGANTE: Permission já vem carregado mesmo sem fixtures o_O
        add_structure_perm = Permission.objects.get(codename='add_structure')
        self.user.user_permissions.add(add_structure_perm)
        
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
        data = {'name': 'test', 'template': tmpl}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(Structure.objects.count(), 1)
        self.assertContains(response, data['name'])
        self.assertContains(response, data['template'].name.split('.')[-1])
        self.assertContains(response, 'id')
        
    def test_save_errors(self):
        url = reverse('tod_structure_ajax_add')
        data = {'name': 'test'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(Structure.objects.count(), 0)
        self.assertContains(response, 'errors')
        
        
class StructureNoPermissions(TestCase):
    
    def test_add(self):
        url = reverse('admin:tv_on_demand_structure_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        
    def test_ajax_add(self):
        url = reverse('tod_structure_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)