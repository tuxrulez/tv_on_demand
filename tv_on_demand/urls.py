#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('tv_on_demand.views',
    url(r'^tv_on_demand/main/(?P<structure_id>\d+)/$', 'main', name='tod_main'),
    url(r'^tv_on_demand/pure-main/(?P<structure_id>\d+)/$', 'pure_main', name='tod_pure_main'),
    url(r'^tv_on_demand/main/children/(?P<father_id>\d+)/$', 'children_of', name='tod_children'),
    url(r'^tv_on_demand/main/video/(?P<row_id>\d+)/(?P<video_id>\d+)/$', 'serve_video', name='tod_serve_video'),
    url(r'^tv_on_demand/structure/add/$', 'structure_add', name='tod_structure_add'),
    url(r'^tv_on_demand/structure/(?P<object_id>\d+)/$', 'structure_change', name='tod_structure_change'),
    url(r'^tv_on_demand/structurerow/ajax-add/$', 'structurerow_ajax_add',
        name='tod_structurerow_ajax_add'),
    url(r'^tv_on_demand/structurerow/ajax-change/(?P<object_id>\d+)/$', 'structurerow_ajax_change',
        name='tod_structurerow_ajax_change'),
    url(r'^tv_on_demand/structurerow/ajax-delete/(?P<object_id>\d+)/$', 'structurerow_ajax_delete',
        name='tod_structurerow_ajax_delete'),
    url(r'^tv_on_demand/live-media/(?P<filename>.+)/$', 'live_media', name='tod_live_media'),
    url(r'^tv_on_demand/live/$', 'live', name='tod_live'),
    url(r'tv_on_demand/do-login/(?P<row_id>\d+)/$', 'do_login', name='tod_login'),
    url(r'tv_on_demand/do-logout/$', 'do_logout', name='tod_logout'),
)
