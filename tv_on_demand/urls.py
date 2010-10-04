#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('tv_on_demand.views',
    url(r'^tv_on_demand/structure/add/$', 'structure_add', name='tod_structure_add'),
    url(r'^tv_on_demand/structure/(?P<object_id>\d+)/$', 'structure_change', name='tod_structure_change'),
    url(r'^tv_on_demand/structurerow/ajax-add/$', 'structurerow_ajax_add',
        name='tod_structurerow_ajax_add'),
    url(r'^tv_on_demand/structurerow/ajax-change/(?P<object_id>\d+)/$', 'structurerow_ajax_change',
        name='tod_structurerow_ajax_change'),
    url(r'^tv_on_demand/structurerow/ajax-delete/(?P<object_id>\d+)/$', 'structurerow_ajax_delete',
        name='tod_structurerow_ajax_delete'),
)