#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from tv_on_demand.models import Skin, Structure, StructureRow

admin.site.register(Skin)
admin.site.register(Structure)
admin.site.register(StructureRow)

