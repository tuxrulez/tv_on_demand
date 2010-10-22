#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import commands
from datetime import date
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from tv_on_demand.models import Structure,StructureRow
from tv_on_demand.helpers import ExportToLog, TodToXml


def create_structure():
    return Structure.objects.create(name='Structure 1',template='template1.swf',external_id='5001')


class HistoryLogTest(TestCase):

    fixtures = ['log_structures.json','log_structurerows.json']

    def make_command(self):
        command = 'python %s/manage.py generate_tod_logs' % settings.MODPATH
        result = commands.getstatusoutput(command)
        return result

    def make_export(self, instance, related_object=None):
        exporter = ExportToLog(related_object=related_object)
        exporter.export()

        log_content = open(exporter.historylog_path, 'r').read()
        os.remove(exporter.historylog_path)

        self.assertTrue(str(instance.pk) in log_content)
        self.assertTrue(instance.name in log_content)

        return exporter

    def test_exec_sucess(self):
        result = self.make_command()
        self.assertEqual(result[0],0)
    
    def test_file_exists_with_relation(self):
        related_object = create_structure()

        ctype = ContentType.objects.get_for_model(related_object)
        instance = Structure.objects.create(name='Structure 1',template='template1.swf',external_id='5002',
                                            content_type=ctype, object_id=related_object.pk)
        instance_rows = StructureRow.objects.filter(structure=instance)

        exporter = self.make_export(instance,related_object)
       
        opts = related_object._meta
        fake_path = '%s/exporter/logs/%s/%s/%s/%s.json' %(settings.MODPATH,opts.app_label,opts.module_name, 
                                                          getattr(related_object, 'slug', str(related_object.pk)), date.today())
        
        self.assertTrue(fake_path in exporter.historylog_path)

    def test_file_exists_without_relation(self):
        instance = create_structure()
        exporter = self.make_export(instance)

        fake_path = '%s/exporter/logs/%s.json' %(settings.MODPATH,date.today())
        self.assertTrue(fake_path in exporter.historylog_path)


class TestTodToXml(TestCase):
    
    fixtures = ['structurerows.json', 'structure.json']
    
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
       self.assertTrue('template' in content)
       self.assertTrue(self.structure_instance.template.path in content)
       
       for row in self.structure_instance.structurerow_set.all():
           self.assertTrue('title' in content)
           self.assertTrue(row.title in content)
           self.assertTrue('label' in content)
           self.assertTrue(row.label in content)

       self.clean_path()

