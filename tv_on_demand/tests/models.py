#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from tv_on_demand.models import Structure, StructureRow
from mediafiles.models import MediaFile
from quizzes.models import Question

#helpers
now = datetime.now()
later = datetime.now() + timedelta(days=10)

def create_structure(name='test name', template='test.swf', **kwargs):
    data = {'name': name, 'template': template}
    data.update(kwargs)
    
    return Structure.objects.create(**data)
    
def create_structurerow(structure=None, title='test title', label='test label',\
                        date_start=now, date_end=later, entry='latest', order=0, **kwargs):
    
    if not structure:
        structure = create_structure()

    data = {'structure': structure, 'title': title, 'label': label, 'date_start': date_start,
            'date_end': date_end, 'entry': entry, 'order': order}
    data.update(**kwargs)
    
    return StructureRow.objects.create(**data)



class StructureModelTest(TestCase):
    
    def test_creation(self):
        instance = create_structure()
        
        self.assertEqual(Structure.objects.count(), 1)
        
        
    def test_generic_relation(self):
        related_object = create_structure()
        ctype = ContentType.objects.get_for_model(related_object)
        instance = create_structure(content_type=ctype, object_id=related_object.pk)
        
        self.assertEqual(instance.content_object.pk, related_object.pk)
        


class StructureRowModelTest(TestCase):
    
    fixtures = ['mediafiles.json', 'quizzes.json']
    
    def test_creation(self):
        mediafile = MediaFile.objects.all()[0]
        question = Question.objects.all()[0]
        instance = create_structurerow(mediafile=mediafile, question=question)
        
        self.assertEqual(StructureRow.objects.count(), 1)
    
    
    
        
