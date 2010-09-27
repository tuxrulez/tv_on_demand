#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from tv_on_demand.models import Structure, StructureRow

admin.site.register(Structure)
admin.site.register(StructureRow)