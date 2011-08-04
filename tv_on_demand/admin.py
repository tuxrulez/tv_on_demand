#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from tv_on_demand.models import Skin, Structure, StructureRow

class StructureAdmin(admin.ModelAdmin):
    list_filter = ['chain', 'store']

class StructureRowAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(Skin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(StructureRow, StructureRowAdmin)

