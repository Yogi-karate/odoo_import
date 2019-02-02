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

class ProductTemplate(Module):
    
    _name = 'product.template'
    _field_list = {'name','type','create_variant'}
    ids = []
    

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf

    def create(self,products,attribute_values,odoo):
        conf = self.conf['products']
        if not conf['columns'] or not attribute_values or not products:
            raise Exception("Invalid Configuration - Cannot find Products to create")
        columns = conf['columns'].upper().split(',')
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        ids = self.model.create(self._create_records(products,attribute_values))
        return ids

    def _create_records(self,products,attribute_values):
        product_list = []
        for product in products:
            record = {}
            record['name'] = product['name'] 
            record['type'] = 'product'
            record['tracking'] = 'serial'
            record['attribute_line_ids'] = self._create_attribute_lines(product['values'],attribute_values)
            product_list.append(record)
        return product_list
    
    def _create_attribute_lines(self,product_values,attribute_values):
        attribute_lines = []
        for vals in product_values:
            attribute,values = vals
            attribute_line = [0,'_',{'attribute_id':attribute_values[attribute]['id'],'value_ids':self._create_value_ids(values,attribute_values[attribute]['values'])}]
            attribute_lines.append(attribute_line)  
        return attribute_lines

    def _create_value_ids(self,product_values,attribute_values):    
        value_ids = []
        value_id = [6,False,[x for x,y in attribute_values if y in product_values]]
        value_ids.append(value_id)
        return value_ids

    def write(self,path):
        pass

    @property
    def get_field_list(self):
        return self._field_list

class ProductProduct(Module):

    _name = 'product.product'
    _field_list = {'name','attribute_id'}

    def __init__(self,conf):
        self.conf = conf

    def get_product_product_list(self,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        model = odoo.env[self._name]
        ids = model.search([])
        ids.sort()
        return ids

    def find_product(self,name,values,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        if not name or not values:
            return
        criteria = [('name','=',name),('attribute_value_ids','in',values)]
        model = odoo.env[self._name]
        ids = model.search(criteria)
        return ids

    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(conf['odoo'])
        model = odoo.env[self._name]
        for lines in range(len(values)):
            for key,vals in values[lines].items():
                model.create([{'attribute_id':key,'name':vals[index]} for index in range(len(vals))])
