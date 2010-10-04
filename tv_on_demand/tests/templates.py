#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template import Template, Context
from tv_on_demand.forms import StructureForm


class StructureTemplateTest(TestCase):
    
    def render(self, extra_context={}):
        t = Template('''{% load structure_tags %}
        {% structure_as_p form 'users' %}
        ''')
        c = Context(extra_context)
        
        return t.render(c)    
    
    def test_structure_as_p(self):
        rendered = self.render({'form': StructureForm()})
        
        self.assertTrue('name' in rendered)
        self.assertFalse('users' in rendered)
        
 
    def test_structure_as_p_errors(self):
        data = {'template': 'test.swf'}
        rendered = self.render({'form': StructureForm(data)})
       
        self.assertTrue('error' in rendered)
