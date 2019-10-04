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


class Pricelist(Module):


    _name = 'product.pricelist'
    _field_list = {'name','type','create_variant'}
    ids = []
    

    def __init__(self,conf):
        if not conf['odoo']:
            raise Exception("Cannot create pricelist")
        self.conf = conf

    def create(self,name,company,odoo):
        print("Hello from pricelist create")
        pricelist = {"active":True,"discount_policy":"with_discount","currency_id":20,"country_group_ids":[[6,False,[]]]}
        pricelist.update({"name":name,"comany_id":company})
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        id_exists = odoo.env[self._name].search([('name','=',name)],limit=1)
        if not id_exists:
            self.model = odoo.env[self._name]
            ids = self.model.create(pricelist)
            return ids
        else:
            _logger.info(" %s Pricelist Already Exists %s",name,id_exists)
            return id_exists[0]

    def write(self,path):
        pass

    @property
    def get_field_list(self):
        return self._field_list

class PriceListComponentType(Module):
    _name = 'dms.price.component'
    _field_list = {'name'}    

    def __init__(self,conf):
        self.conf = conf
    
    def getComponents(self):
        odoo = tools.login(self.conf['odoo'])
        return odoo.env[self._name].search([])

    def create(self,items,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        product_list = []
        for pricelist in items:
            record = {}
            print("the pricelist item is ",pricelist)
            product_list.append(record)
        print(product_list)
        # self.model = odoo.env[self._name]
        # ids = self.model.create(product_list)
        # return ids

class PricelistComponent(Module):
    _name = 'pricelist.component'
    _field_list = {'name'}

    def __init__(self,conf):
        self.conf = conf
    

    def create(self,items,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        product_list = []
        for pricelist in items:
            record = {}
            print("the pricelist item is ",pricelist)
            product_list.append(record)
        print(product_list)
        # self.model = odoo.env[self._name]
        # ids = self.model.create(product_list)
        # return ids

class PricelistItem(Module):

    _name = 'pricelist.item'
    _field_list = {'name','attribute_id'}

    def __init__(self,conf):
        self.conf = conf
        self.components = PriceListComponentType(self.conf).getComponents()
        print(self.components)
        
    
    def create(self,items,pricelist_id,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        product_list = []
        print('The pricelist to be added to is',pricelist_id,len(items))
        #for pricelist in items:
            #record = {}
            #product_list.append(record)
        #print(product_list)
        return 'Done'
        # self.model = odoo.env[self._name]
        # ids = self.model.create(product_list)
        # return ids
