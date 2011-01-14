#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import urllib
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.conf import settings
from mediafiles.models import MediaFile
from tv_on_demand.models import Structure, StructureRow, Skin

FILEPATH = os.path.abspath(os.path.dirname(__file__))

class StructureViewTest(TestCase):
    
    fixtures = ['structures.json', 'skins.json']
    userdata = {'username': 'admin', 'password': 'admin123',
                'email': 'admin@admin.com'}
                
    def setUp(self):
        self.user = User.objects.create_user(**self.userdata)
        # INTRIGANTE: Permission já vem carregado mesmo sem fixtures o_O
        add_structure_perm = Permission.objects.get(codename='add_structure')
        change_structure_perm = Permission.objects.get(codename='change_structure')
        add_row_perm = Permission.objects.get(codename='add_structurerow')
        change_row_perm = Permission.objects.get(codename='change_structurerow')
        delete_row_perm = Permission.objects.get(codename='delete_structurerow')
        self.user.user_permissions.add(add_structure_perm, change_structure_perm,
                                       add_row_perm, change_row_perm, delete_row_perm)
        
        self.client.login(username=self.userdata['username'], password=self.userdata['password'])
        self.skin = Skin.objects.all()[0]
        self.default_data = {'name': 'test add', 'skin': self.skin.pk}
        
    
    def test_add_response(self):
        url = reverse('admin:tv_on_demand_structure_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tv_on_demand/structure_form.html')      
        
        
    def test_add_post(self):
        url = reverse('admin:tv_on_demand_structure_add')
        response = self.client.post(url, self.default_data)

        structure_instance = Structure.objects.get(name=self.default_data['name'])
        self.assertTrue(structure_instance)
        
    def test_change_post(self):
        instance = Structure.objects.all()[0]
        url = reverse('admin:tv_on_demand_structure_change', args=[instance.pk])
        data = {'name': 'changed name', 'skin': self.skin.pk}
        response = self.client.post(url, data)
        
        structure = Structure.objects.get(pk=instance.pk)
        self.assertEqual(structure.name, data['name'])
        self.assertEqual(structure.skin, instance.skin)
 
        
        
class StructureNoPermissions(TestCase):
    
    fixtures = ['structures.json']
    
    def test_add(self):
        url = reverse('admin:tv_on_demand_structure_add')
        data = {}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)        
        
    def test_change(self):
        instance = Structure.objects.all()[0]
        url = reverse('admin:tv_on_demand_structure_change', args=[instance.pk])
        data = {'name': 'another changed name'}
        response = self.client.post(url, data)
        
        structure = Structure.objects.get(pk=instance.pk)
        
        self.assertEqual(structure.name, instance.name)
        self.assertEqual(response.status_code, 302)
        
 

class StructureRowViewTest(TestCase):
    
    fixtures = ['structures.json', 'mediafiles.json', 'structurerows.json']    
    userdata = {'username': 'admin', 'password': '123', 'email': 'admin@admin.com'}
    
    def setUp(self):
        self.user = User.objects.create_user(**self.userdata)
        add_perm = Permission.objects.get(codename='add_structurerow')
        change_perm = Permission.objects.get(codename='change_structurerow')
        delete_perm = Permission.objects.get(codename='delete_structurerow')
        self.user.user_permissions.add(add_perm, change_perm, delete_perm)
        self.client.login(username=self.userdata['username'], password=self.userdata['password'])
        
        structure = Structure.objects.all()[0]
        mediafile = MediaFile.objects.all()[0]
        
        self.default_data = {'structure': structure.pk, 'title': 'test title xdv8', 'label': 'test label',
                             'mediafile': mediafile.pk, 'date_start': '14/05/1989 14:15', 'external_id': 0,
                             'date_end': '21/12/2098 21:10', 'order': 0, 'users': [self.user.pk]}    
    
    def test_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = self.default_data
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        
        
    def test_wrong_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = self.default_data
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
        
        
    def test_ajax_add_save(self):
        url = reverse('tod_structurerow_ajax_add')
        data = self.default_data
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(StructureRow.objects.filter(title=data['title']).count(), 1)
        self.assertContains(response, data['title'])
        self.assertContains(response, data['label'])
        self.assertContains(response, data['date_start'])
        self.assertContains(response, data['date_end'])
        self.assertContains(response, 'order')
        self.assertContains(response, 'users')
        self.assertContains(response, 'structure')
        self.assertContains(response, 'mediafile')
        self.assertContains(response, 'entry')
        self.assertContains(response, 'parent')
    
    def test_wrong_ajax_add_save(self):
        url = reverse('tod_structurerow_ajax_add')
        data = self.default_data
        data['order'] = None
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(StructureRow.objects.filter(title=data['title']).count(), 0)
        self.assertContains(response, 'errors')
        
    def test_ajax_change_response(self):
        structurerow = StructureRow.objects.all()[0]
        url = reverse('tod_structurerow_ajax_change', args=[structurerow.pk])
        data = self.default_data
        data['title'] = 'new title is gozo clown =D'
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], StructureRow.objects.get(pk=structurerow.pk).title)
        
    def test_wrong_ajax_change(self):
        structurerow = StructureRow.objects.all()[0]
        url = reverse('tod_structurerow_ajax_change', args=[structurerow.pk])
        data = self.default_data
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 403)
        
    def test_wrong_id_ajax_change(self):
        url = reverse('tod_structurerow_ajax_change', args=[666])
        data = self.default_data
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
        
    def test_ajax_delete_response(self):
        structurerow = StructureRow.objects.all()[0]
        url = reverse('tod_structurerow_ajax_delete', args=[structurerow.pk])
        response = self.client.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StructureRow.objects.filter(pk=structurerow.pk).count(), 0)
        
    def test_wrong_ajax_delete(self):
        url = reverse('tod_structurerow_ajax_delete', args=[666])
        response = self.client.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
        
        
        
class StructureRowNoPermissions(TestCase):
    
    fixtures = ['structurerows.json']
    
    def test_ajax_add_response(self):
        url = reverse('tod_structurerow_ajax_add')
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        
    def test_ajax_change_response(self):
        structurerow = StructureRow.objects.all()[0]
        url = reverse('tod_structurerow_ajax_change', args=[structurerow.pk])
        data = {}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        
    def test_ajax_delete_response(self):
        structurerow = StructureRow.objects.all()[0]
        url = reverse('tod_structurerow_ajax_delete', args=[structurerow.pk])
        response = self.client.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StructureRow.objects.filter(pk=structurerow.pk).count(), 1)
        
        
class LiveMediaViewTest(TestCase):
    
    def create_fake_media(self, name='hi_im_live.avi.0003'):
        live_dir = os.path.join(settings.MODPATH, 'importer', 'tv_on_demand', 'live')
        if not os.path.exists(live_dir):
            os.makedirs(live_dir)
            
        live_file_path = os.path.join(live_dir, name)
        if os.path.exists(live_file_path):
            return live_file_path
            
        live_file = open(live_file_path, 'wb')
        live_file.write('fake content')
        live_file.close()
        
        return live_file_path                
    
    def setUp(self):
        self.url = reverse('tod_live_media', args=['anything.avi.0001'])
    
    def test_live_response(self):
        response = self.client.get(self.url)        
        self.assertEqual(response.status_code, 403)
        
    def test_live_content(self):        
        file_path = self.create_fake_media()
        filename = file_path.split('/')[-1]
        url = reverse('tod_live_media', args=[filename])
        response = self.client.get(url)
        
        expected_mimetype = 'video/x-msvideo'
        response_mimetype = response.items()[0][1]
        
        self.assertEqual(expected_mimetype, response_mimetype)
        self.assertEqual(response.status_code, 200)
        
        os.remove(file_path)
        
        
class LiveViewTest(TestCase):
    
    def test_response(self):
        url = reverse('tod_live')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        
        
        
        
        
        
        

        
