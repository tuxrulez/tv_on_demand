#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('tv_on_demand.views',
    url(r'^tv_on_demand/structure/add/$', 'structure_add', name='tod_structure_add'),
    url(r'^tv_on_demand/structure/ajax-add/$', 'structure_ajax_add', name='tod_structure_ajax_add'),
)