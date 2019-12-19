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
        ids = self._create_records(products,attribute_values)
        _logger.debug(" %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",ids)
        return ids

    def _create_records(self,products,attribute_values):
        product_list = []
        for product in products:
            product_name = product['name'].strip()
            pro = self.model.search([('name','=',product_name)],limit=1)
            if not pro:
                record = {}
                record['name'] = product_name
                record['type'] = 'product'
                record['tracking'] = 'serial'
                # redo - remove hard coding later fetch from db
                record['categ_id'] = 4
                record['attribute_line_ids'] = self._create_attribute_lines(product['values'],attribute_values,[])
                x = self.model.create(record)
                product_list.append(x)
            else:
                record = {}
                record['attribute_line_ids'] = self._create_attribute_lines(product['values'],attribute_values,pro)
                self.model.browse(pro[0]).write(record)
                product_list.append(pro[0])
        return product_list
    
    def _create_attribute_lines(self,product_values,attribute_values,pro):
        attribute_lines = []
        for vals in product_values:
            attribute,values = vals
            if len(pro) > 0:
                    od = tools.login(self.conf['odoo'])
                    model = od.env['product.template.attribute.value']
                    mod = od.env['product.template.attribute.line']
                    pro_att_val = od.env['product.attribute.value']
                    line = mod.search([('product_tmpl_id','=',pro[0]),('attribute_id','=',attribute_values[attribute]['id'])])
                    if len(line) <= 0:
                        attribute_line = [0,'_',{'attribute_id':attribute_values[attribute]['id'],'value_ids':self._create_value_ids(values,attribute_values[attribute]['values'],pro,attribute_values[attribute]['id'])}]
                        attribute_lines.append(attribute_line) 
                    else:
                        attribute_line = [1,line[0],{'attribute_id':attribute_values[attribute]['id'],'value_ids':self._create_value_ids(values,attribute_values[attribute]['values'],pro,attribute_values[attribute]['id'])}]
                        attribute_lines.append(attribute_line) 
            else:
                    attribute_line = [0,'_',{'attribute_id':attribute_values[attribute]['id'],'value_ids':self._create_value_ids(values,attribute_values[attribute]['values'],pro,attribute_values[attribute]['id'])}]
                    attribute_lines.append(attribute_line)  
        return attribute_lines

    def _create_value_ids(self,product_values,attribute_values,pro,attribute_id):
            od = tools.login(self.conf['odoo'])
            mod = od.env['product.template.attribute.line']
            value_ids = []
            temp = []
            if len(pro)>0:
                val_ids = mod.search_read([('product_tmpl_id','=',pro[0]),('attribute_id','=',attribute_id)])
                for val_id in val_ids:
                    for i in val_id['value_ids']:
                        #value_ids.append([6,False,i])
                        temp.append(i)
            value_id = []
            for x in product_values:
                # _logger.debug("the temp values in value ids %s %s",temp,x)
                # _logger.debug("the attribute values in value ids %s",attribute_values)
                if attribute_values[x] not in temp:
                    temp.append(attribute_values[x])
                    #value_id = [6,False,[attribute_values[x]]]
            value_id = [6,False,temp]
            value_ids.append(value_id)
            _logger.debug("the values ids in create value ids %s",value_ids)
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
        self.product_cache = None

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
   
    def search_for_duplicate(self,product):
        vals = []
        #_logger.debug("the product is %s",product)
        if self.product_cache:
            product_key = product['NAME']+'_'+product['COLOR']+'_'+product['VARIANT']
           # _logger.debug("the product key is %s",product_key)
            if product_key in self.product_cache:
                product_id = self.product_cache[product_key]
                #_logger.debug("the product from cache is %s",product_id)
                return product_id

    def create(self,products,attributes,attribute_columns,odoo):
        ids = []
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        if not self.product_cache:
            product_cache = {}
            product_template_ids = list(set([int(x['product_tmpl_id']) for x in products ]))
            _logger.debug("the product ids are %s",product_template_ids)
            mod = odoo.execute_kw(self._name,'search_read',[[('product_tmpl_id','in',product_template_ids)]],{'fields':['id','name','color_value','variant_value']})
            product_cache = {x['name']+'_'+x['color_value']+'_'+x['variant_value']:x['id'] for x in mod}
            _logger.debug("product search result %s",product_cache)
            self.product_cache = product_cache
        self.model = odoo.env[self._name]
        records = []
        pos = 0
        for product in products:
            dup = self.search_for_duplicate(product)
            if dup:
                ids.append(dup)
            else:
                record = {}
                record['product_tmpl_id'] = product['product_tmpl_id']
                record['attribute_value_ids'] = self.create_attribute_value_ids(product,attributes,attribute_columns)
                #idm = self.model.create(record)
                record['pos'] = pos
                records.append(record)
                ids.append(0)
            pos +=1
        _logger.info(" Creating %s New products ",len(records))
        new_ids = self.model.create(records)
        for index in range(len(records)):
            ids[records[index]['pos']] = new_ids[index]
        return ids

    def create_attribute_value_ids(self,product,attributes,attribute_columns):
        value_ids = []
        for column in attribute_columns:
            value_id = attributes[column]['values'][product[column]]
            value_ids.append(value_id)
        _logger.debug(" %s --------------------------------------------------column",value_ids)
        return [(6,'_',value_ids)]
