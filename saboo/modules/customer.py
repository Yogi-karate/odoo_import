# -*- coding: UTF-8 -*-
##############################################################################
#
#    Saboo
#    Copyright (C) 2014 Rammohan Tangirala.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""The `saboo` module defines the :classes:`XLS` and 'Odoo' class.

The :class:`ODOO` class is the entry point to manage `Odoo` servers using odoo RPC
You can use this one to write `Python` programs that performs a variety of
automated jobs that communicate with a `Odoo` server.
"""
import saboo
import saboo.tools as tools
from .module import Module
import pandas as pd
import logging

_logger = logging.getLogger(__name__)

class Customer(Module):
    
    _name = 'res.partner'
    ids = []
    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf

    def create(self,customers,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        print(customers)
        batches = tools.batcher(customers,2000)
        _logger.debug(len(batches.keys()))
        all_ids=[]
        for counter in batches.keys():
            partial = customers[batches[counter][0]:batches[counter][1]]
            ids = self.model.create(partial)
            all_ids = all_ids+ids
            print(ids)
        all_ids.sort()    
        return all_ids

    def write(self,path):
        pass

    @property
    def get_field_list(self):
        return self._field_list

class Vendor(Customer):

    def __init__(self,conf):
        self.conf = conf

    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        if not values or len(values) < 1:
            return
        for vendor in values:
            if not vendor['supplier'] == True or not vendor['is_company'] == 'True':
                print("Invalid Vendor values - creation FAILED")
                return
        model = odoo.env[self._name]
        model.create(values)

class Lead(Module):
    def __init__(self,conf):
        self.conf = conf

    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        if not values or len(values) < 1:
            return
        for lead in values:
            if not lead['partner_id']:
                print("Invalid Enquiry - creation FAILED")
                return
        model = odoo.env[self._name]
        model.create(values)
