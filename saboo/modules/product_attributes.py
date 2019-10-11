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

class ProductAttributes(Module):
    
    _name = 'product.attribute'
    _field_list = {'name','type','create_variant'}
    ids = []

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf

    def create(self,attribute_values,odoo):
        conf = self.conf['attributes']
        if not conf['columns'] or not conf['fields']:
            raise Exception("Invalid Configuration - Cannot find Attributes to create")
        columns = conf['columns'].upper().split(',')
        values = ProductAttributeValues(self.conf)
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        model = odoo.env[self._name]
        attribute_list = self._create_records(columns)
        write_ids = []
        for attribute in attribute_list:
            att = model.search([('name','=',attribute['name'])])
            if len(att) == 0:
                att = model.create(attribute)
                self.ids.append(att)
            else:
                self.ids.append(att[0])
        return values.create([{'name':columns[index],'id':self.ids[index],'values':attribute_values[columns[index]]} for index in range(len(columns))],odoo)

    def _create_records(self,columns):
        attribute_list = []
        for attribute in columns:
            record = {}
            record['name'] = attribute 
            record['type'] = 'select'
            record['create_variant'] = 'dynamic'
            print(record)
            attribute_list.append(record)
        return attribute_list
    
    def write(self,path):
        pass

    @property
    def get_field_list(self):
        return self._field_list

class ProductAttributeValues(Module):

    _name = 'product.attribute.value'
    _field_list = {'name','attribute_id'}

    def __init__(self,conf):
        self.conf = conf
   
    def get_attribute_values(self,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        conf = self.conf['attributes']
        if not conf['columns'] or not conf['fields']:
            raise Exception("Invalid Configuration - Cannot find Attributes to create")
        columns = conf['columns'].upper().split(',')
        model = odoo.env[self._name]
        res = {}
        for column in columns:
            attr = odoo.env['product.attribute']
            attr_id = attr.search([('name','=',column)],limit=1)
            value_ids = attr.browse(attr_id).value_ids
            if value_ids:
                values = []
                for value_id in value_ids:
                    print(value_id)
                    print(value_id.name)
                    values.append(value_id.name)
                res[column] = {'id':attr_id[0],'values':{values[index]:value_ids[index].id for index in range(len(value_ids))}}
        return res


    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(conf['odoo'])
        model = odoo.env[self._name]
        res = {}
        for lines in range(len(values)):
            ids = []
            attr_id = values[lines]['id']
            name = values[lines]['name']
            vals = values[lines]['values']
            print(name,vals)
            count = 0
            for val in vals:
                mod = model.search([('attribute_id','=',attr_id),('name','=',val)])
                if not mod:
                    record = {}
                    record['name'] = val
                    record['attribute_id'] = attr_id
                    ids.append(model.create(record))
                else:
                    ids.append(mod[0])
            #ids = model.create([{'attribute_id':attr_id,'name':vals[index]} for index in range(len(vals))])
            res[name] = {'id':attr_id,'values':{vals[index]:ids[index] for index in range(len(ids))}}
        return res