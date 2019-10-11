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
        ids = self._create_records(products,attribute_values,self.model)
        print(ids,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        return ids

    def _create_records(self,products,attribute_values,model):
        product_list = []
        for product in products:
            pro = model.search([('name','=',product['name'])])
            if len(pro) <= 0:
                record = {}
                record['name'] = product['name'] 
                record['type'] = 'product'
                record['tracking'] = 'serial'
                record['attribute_line_ids'] = self._create_attribute_lines(product['values'],attribute_values,[])
                x = model.create(record)
                product_list.append(x)
            else:
                record = {}
                record['attribute_line_ids'] = self._create_attribute_lines(product['values'],attribute_values,pro)
                model.write(pro,record)
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
                if attribute_values[x] not in temp:
                    temp.append(attribute_values[x])
                    #value_id = [6,False,[attribute_values[x]]]
            value_id = [6,False,temp]
            value_ids.append(value_id)
            print(value_ids)
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
    def search_for_duplicate(self,product,attributes,attribute_columns,odoo):
        duplicate = -1
        vals = []
        val_ids = []
        for column in attribute_columns:
                vals.append(product[column])
                val_ids.append(attributes[column]['values'][product[column]])
        product_products = self.model.search([('product_tmpl_id','=',int(product['product_tmpl_id'])),('color_value','=',vals[0]),('variant_value','=',vals[1])])    
        if len(product_products) > 0:
            return product_products
        # for x in product_products:
        #     if vals[0] in x['attribute_value_ids'] and vals[1] in x['attribute_value_ids']:
        #                 duplicate = x['id']
        #     if duplicate > 0:
        #             return [duplicate]
        return val_ids
    def create(self,products,attributes,attribute_columns,odoo):
        ids = []
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        product_list = []
        for product in products:
            dup = self.search_for_duplicate(product,attributes,attribute_columns,odoo)
            if len(dup) == 1:
                ids.append(dup[0])
            else:
                record = {}
                record['name'] = product['NAME']
                record['product_tmpl_id'] = product['product_tmpl_id']
                record['attribute_value_ids'] = [(6,'_',dup)]
                idm = self.model.create(record)
                ids.append(idm)
                # record = {}
                # record['name'] = product['NAME']
                # record['product_tmpl_id'] = product['product_tmpl_id']
                # record['attribute_value_ids'] = self.create_attribute_value_ids(product,attributes,attribute_columns)
                # idm = self.model.create(record)
                # ids.append(idm)
        return ids

    def create_attribute_value_ids(self,product,attributes,attribute_columns):
        
        value_ids = []
        for column in attribute_columns:
           # print(attributes[column]['values'],"-------------------------column")
            value_id = attributes[column]['values'][product[column]]
            value_ids.append(value_id)
        print(value_ids,"--------------------------------------------------column")
        return [(6,'_',value_ids)]

    # def create(self,values,odoo):
    #     if not odoo:
    #         odoo = tools.login(conf['odoo'])
    #     model = odoo.env[self._name]
    #     for lines in range(len(values)):
    #         for key,vals in values[lines].items():
    #             model.create([{'attribute_id':key,'name':vals[index]} for index in range(len(vals))])
