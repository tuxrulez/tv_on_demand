#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from tv_on_demand.models import Structure, StructureRow, Skin

class StructureAdmin(admin.ModelAdmin):
    
    list_filter = ['mediadatabase', 'skin']
    

class StructureRowAdmin(admin.ModelAdmin):
    list_filter = ['structure']


admin.site.register(Skin)
admin.site.register(Structure,StructureAdmin)
admin.site.register(StructureRow, StructureRowAdmin)
