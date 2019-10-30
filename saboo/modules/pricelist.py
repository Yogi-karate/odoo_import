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
        if id_exists:
            _logger.info(" %s Pricelist Already Exists %s",name,id_exists)
            old_pricelist = odoo.env[self._name].browse(id_exists)
            old_pricelist.unlink()
        self.model = odoo.env[self._name]
        ids = self.model.create(pricelist)
        return ids

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
        return odoo.execute_kw(self._name,'search_read',[],{'fields':['id','name']})
        #return [x['name'] for x in vals]

    def create(self,items,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        ids = self.model.create(items)
        return ids

class PricelistComponent(Module):
    _name = 'pricelist.component'
    _field_list = {'name'}

    def __init__(self,conf):
        self.conf = conf

    def create(self,items,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        ids = self.model.create(items)
        return ids

class PricelistItem(Module):

    _component = 'dms_price_component'
    _component_field_list = {"name":"", "description":""}
    _name = 'product.pricelist.item'
    _field_list = {"applied_on":"0_product_variant","min_quantity":0,"compute_price":"fixed",
    "base":"list_price","price_discount":0,"pricelist_id":66,"product_id":2011,
    "date_start":"2019-11-01","fixed_price":2500000,"percent_price":0}
 
    def __init__(self,conf):
        self.conf = conf
        self.components = PriceListComponentType(self.conf).getComponents()
        print("components",self.components)
        
    def findProduct(self,model,variant,color):
        model_name = 'product.product'
        odoo = tools.login(self.conf['odoo'])
        if odoo and model and variant and color:
            ids = odoo.env[model_name].search([('product_tmpl_id','=',model),('variant_value','=',variant),('color_value','=',color)])
            return ids

    def create(self,items,pricelist_id,component_columns,odoo):
        #print("items",items)
        components = PriceListComponentType(self.conf).getComponents()# to fetch update data from table
        components_names = [x['name'] for x in self.components]
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        for comp in component_columns:
            if not comp in components_names:
                print("comp",comp)
                component_fields = self._component_field_list
                component_fields.update({"name":comp,"description":comp })
                PriceListComponentType(self.conf).create(component_fields,None)
        components = PriceListComponentType(self.conf).getComponents()
        price_lists = []        
        for pricelist in items:
            pricelist_items = {}
            fields = self._field_list.copy()
            fields.update({"fixed_price":str(pricelist['Ex S/R Price']), "pricelist_id":pricelist_id, "product_id" : pricelist['product_id']})
            pricelist_items.update({'item':fields})
            item_components = [ {'item_id':'','type_id':[x['id'] for x in components if x['name'] == comp][0],
                    'price':pricelist[comp]} for comp in component_columns]
            #_logger.debug("the components %s",item_components)
            pricelist_items.update({'components':item_components})
            price_lists.append(pricelist_items)
        price_list_item_ids = self.model.create([ x['item'] for x in price_lists])
        for index in range(len(price_lists)):
            components = price_lists[index]['components']
            for component in components:
                component.update({'item_id':price_list_item_ids[index],'mandatory':True})
            price_lists[index].update({'item_id':price_list_item_ids[index]})
        final_comps = []
        for pricelist in price_lists:
            final_comps = final_comps + pricelist['components']
        component_ids = PricelistComponent(self.conf).create(final_comps,None)
        return price_lists

            
           