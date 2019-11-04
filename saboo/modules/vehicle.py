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
import threading


_logger = logging.getLogger(__name__)

class Vehicle(Module):

    _name = 'vehicle'

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create vehicles")
        self.conf = conf
    
    def get_order_ids(self,vehicle_list):
        odoo = tools.login(self.conf['odoo'])
        name = 'sale.order'
        model = odoo.env[name]
        order_list = odoo.execute_kw(name,'search_read',[[('name','in',[x['ref'] for x in vehicle_list])]],{'fields':['id','name']})
        return {x['name']:x['id'] for x in order_list}

    def create(self,vehicles,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        veh_list = []
        sale_orders = self.get_order_ids(vehicles)
        #print("sale order cache",sale_orders)
        vehicle_names = [vehicle['name'] for vehicle in vehicles]
        duplicate_list = odoo.execute_kw(self._name,'search_read',[[('name','in',vehicle_names)]],{'fields':['id','name']})
        result = {x['name']:x['id'] for x in duplicate_list}   
        for vehicle in vehicles:    
            if result.get(vehicle.get('name')):
                continue
            else:
                if vehicle['ref'] and vehicle['ref'] in sale_orders:
                    print("setting order ids in vehicle")
                    vehicle['order_id'] = sale_orders[vehicle['ref']]
                veh_list.append(vehicle)
        _logger.info("Creating %s new vehicles",len(veh_list))
        odoo.run(self._name,'create',veh_list)

class Inventory(Module):

    _name = 'mass.order.confirm'

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create vehicles")
        self.conf = conf

    def confirm_purchase_orders(self,inventories,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        odoo.run(self._name,'confirm_purchase_orders',inventories)

    def confirm_sale_orders(self,inventories,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        odoo.run(self._name,'confirm_sale_orders',inventories)
        
        
