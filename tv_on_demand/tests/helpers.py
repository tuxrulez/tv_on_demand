#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import commands
from datetime import date
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mediafiles.models import MediaFile
from tv_on_demand.models import Structure,StructureRow,Skin
from tv_on_demand.helpers import ExportToLog, TodToXml, XmlToTod


class TestTodToXml(TestCase):
    
    fixtures = ['structurerows.json', 'structures.json', 'skins.json', 'mediafiles.json']
    
    def setUp(self):
        self.structure_instance = Structure.objects.all()[0]
        self.exporter = TodToXml(structure=self.structure_instance)
        
    def clean_path(self):
       os.remove(self.exporter.xml_path)
       try:
           os.rmdir(self.exporter.save_path)
       except OSError:
           pass
    
    def test_save_path(self):
        expected_path = os.path.join(settings.MODPATH, 'exporter', 'tv_on_demand')        
        self.assertEqual(self.exporter.save_path, expected_path)
        
    def test_save_custom_path(self):
        structure_modulename = self.structure_instance._meta.module_name
        
        custom_exporter = TodToXml(structure=self.structure_instance, model_ref=Structure)               
        custom_expected_path = os.path.join(settings.MODPATH, 'exporter', 'tv_on_demand', structure_modulename)

        self.assertEqual(custom_exporter.save_path, custom_expected_path)
        
    def test_xml_path(self):
        expected_path = os.path.join(self.exporter.save_path, 'structure.xml')
        
        self.assertEqual(self.exporter.xml_path, expected_path)
        
    def test_save(self):
        self.exporter.save()        
        self.assertTrue(os.path.exists(self.exporter.xml_path))
        self.clean_path()
        
    def test_content(self):
       self.exporter.save()
       content = open(self.exporter.xml_path, 'r').read()
       
       self.assertTrue('structure' in content)
       self.assertTrue(str(self.structure_instance.pk) in content)
       self.assertTrue('name' in content)
       self.assertTrue(self.structure_instance.name in content)
       self.assertTrue('skin' in content)
       self.assertTrue(self.structure_instance.skin.css_style.url in content)
       self.assertTrue('company_logo' in content)
       self.assertTrue(self.structure_instance.skin.company_logo.url in content)
       
       for row in self.structure_instance.structurerow_set.all():
           self.assertTrue('title' in content)
           self.assertTrue(row.title in content)
           self.assertTrue('label' in content)
           self.assertTrue(row.label in content)

       self.clean_path()

       
class TestXmlToTod(TestCase):
    
    fixtures = ['mediafiles.json', 'structures.json', 'structurerows.json',
                'skins.json']
                
    def test_import(self):
        structure = Structure.objects.all()[0]
        ini_mediafiles_number = structure.structurerow_set.filter(mediafile__isnull=False).count()
        ini_rows_number = structure.structurerow_set.all().count()
        exporter = TodToXml(structure=structure)
        exporter.save()
        
        # clean all data
        Skin.objects.all().delete()
        MediaFile.objects.all().delete()
        Structure.objects.all().delete()
        StructureRow.objects.all().delete()
        
        importer = XmlToTod(xml_path=exporter.xml_path)
        importer.save()
        
        self.assertEqual(Skin.objects.count(), 1)
        self.assertEqual(Structure.objects.count(), 1)
        
        new_skin = Skin.objects.all()[0]
        new_structure = Structure.objects.all()[0]
        
        self.assertEqual(new_skin.external_id, structure.skin.pk)
        self.assertEqual(new_skin.title, structure.skin.title)
        self.assertEqual(new_skin.slug, structure.skin.slug)
        self.assertEqual(new_skin.css_style, structure.skin.css_style)
        self.assertEqual(new_structure.external_id, structure.pk)
        self.assertEqual(new_structure.skin.slug, structure.skin.slug)
        self.assertEqual(new_structure.name, structure.name)

        self.assertEqual(StructureRow.objects.count(), ini_rows_number)
        self.assertEqual(new_structure.structurerow_set.filter(mediafile__isnull=False).count(), ini_mediafiles_number)       
        
        # clean trash
        os.remove(exporter.xml_path)
