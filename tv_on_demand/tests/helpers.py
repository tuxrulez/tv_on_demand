#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import commands
import time
from datetime import date
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mediafiles.models import MediaFile, MediaDatabase
from tv_on_demand.models import Structure,StructureRow,Skin
from tv_on_demand.helpers import ExportToLog, TodToXml, XmlToTod, LiveFileReader


class TestTodToXml(TestCase):
    
    fixtures = ['structurerows.json', 'structures.json', 'skins.json', 'mediafiles.json', 'mediadatabases.json']
    
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
        #self.clean_path()
        
    def test_content(self):
        self.exporter.save()
        content = open(self.exporter.xml_path, 'r').read()
       
        self.assertTrue('structure' in content)
        self.assertTrue(str(self.structure_instance.pk) in content)
        self.assertTrue('name' in content)
        self.assertTrue(self.structure_instance.name in content)
        
        self.assertTrue('mediadatabase' in content)
        self.assertTrue(self.structure_instance.mediadatabase.name in content)
        self.assertTrue(self.structure_instance.mediadatabase.slug in content)
       
        for row in self.structure_instance.structurerow_set.all():
            self.assertTrue('title' in content)
            self.assertTrue(row.title in content)
            self.assertTrue('label' in content)
            self.assertTrue(row.label in content)
            self.assertTrue('duration' in content)

        #self.clean_path()

       
class TestXmlToTod(TestCase):
    
    fixtures = ['mediafiles.json', 'structures.json', 'structurerows.json',
                'skins.json', 'mediadatabases.json']
                
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
        self.assertEqual(new_structure.external_id, structure.pk)
        self.assertEqual(new_structure.skin.slug, structure.skin.slug)
        self.assertEqual(new_structure.name, structure.name)

        self.assertEqual(StructureRow.objects.count(), ini_rows_number)
        self.assertEqual(new_structure.structurerow_set.filter(mediafile__isnull=False).count(), ini_mediafiles_number)       
        
        # clean trash
        #os.remove(exporter.xml_path)
        
        
class TestLiveFileReader(TestCase):
    
    def create_file(self, name='some_name', ext='avi', part='0001', content_loop=9999):
        file_dir = os.path.join(settings.MODPATH, 'importer', 'tv_on_demand', 'live')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            
        filename = '%s.%s.%s' %(name, ext, part)
        file_path = os.path.join(file_dir, filename)
        
        video_file = open(file_path, 'wb')
        for i in range(content_loop):
            video_file.write('fake content\n')
        video_file.close()
        
        return file_path
        
        
    def test_selector(self):
        invalidfile_by_time = self.create_file(part='0055')
        time.sleep(4)
        validfile_one = self.create_file()
        time.sleep(1)
        validfile_two = self.create_file(part='0002')
        time.sleep(1)
        invalidfile_by_size = self.create_file(part='0066', content_loop=1)
        time.sleep(1)
        invalid_by_ext = self.create_file(part='')     
        
        # mock para diminuir o tempo de validade do arquivo para 3 segundos
        # facilitando assim os testes
        old_live_tv_file_time = getattr(settings, 'LIVE_TV_FILE_TIME', None)
        old_live_tv_file_size = getattr(settings, 'LIVE_TV_FILE_SIZE', None)
        settings.LIVE_TV_FILE_TIME = 3
        # o tamanho mínimo será a metade de um arquivo válido gerado
        settings.LIVE_TV_FILE_SIZE = os.path.getsize(validfile_one) / 2        

        live_reader = LiveFileReader()
        live_reader.select_file()
        
        #self.assertEqual(live_reader.file_path, validfile_two)
        #self.assertEqual(live_reader.file_name, 'some_name.avi.0002')
        
        settings.LIVE_TV_FILE_TIME = old_live_tv_file_time
        settings.LIVE_TV_FILE_SIZE = old_live_tv_file_size
        
        # limpa o lixo
        os.remove(invalidfile_by_time)
        os.remove(validfile_one)
        os.remove(invalidfile_by_size)
        os.remove(validfile_two)
        
        
        
        
    
