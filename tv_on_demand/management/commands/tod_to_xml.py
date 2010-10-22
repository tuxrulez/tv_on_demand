#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from tv_on_demand.helpers import TodToXml

class Command(BaseCommand):
    ''' This command do not anything by itself, it should be extended 
        model_ref - Should be your related model_ref
        instance - The instance of Structure
    '''

    model_ref = None
    instance = None
    rootpath = None

    def handle(self, **options):
        if not self.instance:
            raise NotImplementedError, 'you should provide a structure instance'
        
        exporter = TodToXml(self.instance, model_ref=self.model_ref,rootpath=self.rootpath)
        exporter.save()

