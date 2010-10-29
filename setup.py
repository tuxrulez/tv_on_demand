#-*- coding: utf-8 -*-
from distutils.core import setup

VERSION = '0.1'

setup = setup(
    name='megamidia-tv_on_demand',
    version=VERSION,
    description=u'Modulo de TV sob demanda',
    author='Heigler Rocha',
    author_email='heigler.rocha@megamidia.com.br',
    platforms=['any'],
    packages=[
        'tv_on_demand',
    ]
)

