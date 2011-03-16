#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyamf.remoting.client import RemotingService as RE

url = 'http://10.0.100.73/admin/tv_on_demand/amf-structure/'
gw = RE(url)
service = gw.getService('structure')

print service.rows({'structure_id': 1})
print service.rows({'structure_id': 1, 'parent_id': 2})
print service.verify_user({'row_id': 1})
print service.login({'row_id': 1, 'username': 'admin', 'password': 'admin123'})
