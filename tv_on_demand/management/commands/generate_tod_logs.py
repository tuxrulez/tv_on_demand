# -*- coding:utf-8 -*-

import os
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from tv_on_demand.helpers import ExportToLog

class Command(BaseCommand):

    def handle(self, **options):
        exporter = ExportToLog()
        exporter.export()

        if os.path.exists(exporter.historylog_path):
            print u'Log gerado com sucesso: ' 
            print exporter.historylog_path
        else: 
            print u'Ocorreu algum erro durante a geração dos logs...'

