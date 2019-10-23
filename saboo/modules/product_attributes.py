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

class ProductAttributes(Module):
    
    _name = 'product.attribute'
    _field_list = {'name','type','create_variant'}
    ids = []

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf

    def create(self,attribute_values,odoo):
        _logger.debug("########################################################")
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
            _logger.debug("llllllllllllllllllllllllllllllllllllllllllllllllllll %s",attribute['name'])
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
            _logger.debug('Attribute record %s',record)
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
        self.attribute_values = None
   
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
                    _logger.debug("the values id in get atribs %s",value_id)
                    _logger.debug("the values name in get atribs %s",value_id.name)
                    values.append(value_id.name)
                res[column] = {'id':attr_id[0],'values':{values[index]:value_ids[index].id for index in range(len(value_ids))}}
        return res


    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(conf['odoo'])
        if not self.attribute_values:
            attributes = {}
            for lines in range(len(values)):
                name = values[lines]['name']
                attr_id = values[lines]['id']
                mod = odoo.execute_kw(self._name,'search_read',[[('attribute_id','=',attr_id)]],{'fields':['id','name']})
                result = {x['name']:x['id'] for x in mod}
                attributes.update({name:result})
                _logger.debug("attribute values in cache %s",attributes)
            self.attribute_values = attributes
        model = odoo.env[self._name]
        res = {}
        for lines in range(len(values)):
            ids = []
            records = []
            attr_id = values[lines]['id']
            name = values[lines]['name']
            vals = values[lines]['values']
            record_pos = {}
            pos = 0
            for val in vals:
                cached_id = False
                if self.attribute_values:
                    if name in self.attribute_values and val in self.attribute_values[name]:
                        cached_id = self.attribute_values[name][val]
                        _logger.debug("attribute found in cache %s",cached_id)
                if not cached_id:
                        if not val in record_pos:
                            record = {}
                            record['name'] = val
                            record['attribute_id'] = attr_id
                            record['pos'] = [pos]
                            _logger.debug("attribute record %s",record)
                            records.append(record)
                            record_pos[val] = record 
                        else:
                            record_pos[val]['pos'].append(pos)  
                        # Inserting dummy value   
                        ids.append(0)
                else:
                    ids.append(cached_id)
                pos += 1
            
            if records:
                new_ids = model.create(records)
                _logger.debug("the new ids created %s",new_ids)
                for index in range(len(records)):
                    for posn_id in records[index]['pos']: 
                        ids[posn_id] = new_ids[index]
            _logger.debug("the ids created %s",ids)

            #ids = model.create([{'attribute_id':attr_id,'name':vals[index]} for index in range(len(vals))])
            res[name] = {'id':attr_id,'values':{vals[index]:ids[index] for index in range(len(ids))}}
        return res