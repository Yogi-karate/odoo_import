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

class Customer(Module):
    
    _name = 'res.partner'
    ids = []
    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf
        self.max_records = int(conf['customers']['max_records'])
        self.batch_size = int(conf['customers']['batch_size'])
    
    def get_customer_list(self):
        odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        ids = model.search([('customer','=',True)])
        ids.sort()
        return ids
            
    def create(self,customers,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        all_ids=[]
        if len(customers) > self.max_records:
            thread_list = {}
            batches = tools.batcher(customers,self.batch_size)
            _logger.debug("Number OF Batches is "+str(len(batches.keys())))
            for counter in batches.keys():
                _logger.debug("Running Batch no : " + str(counter+1))
                partial = customers[batches[counter][0]:batches[counter][1]]
                thread = CustomerThread("Thread-"+str(counter),self._name,self.conf,partial)
                thread_list[counter] = thread
            # Start new Threads
            for key in thread_list.keys():
                thread_list[key].start()
            for key in thread_list.keys():
                thread_list[key].join()
            _logger.info("Exiting Main Thread")
        else:
             self.model.create(customers)
        return self.get_customer_list()

    def write(self,path):
        pass

    @property
    def get_field_list(self):
        return self._field_list

class CustomerThread(threading.Thread):

    def __init__(self,thread_name,model_name,conf,customers):
        threading.Thread.__init__(self)
        self.conf = conf
        self.customers = customers
        self.batch_size = int(conf['customers']['max_thread_records'])
        self.name = thread_name
        self.model_name = model_name

    def run(self):
        _logger.info("Starting " + self.name)
        self.create_customers()
        _logger.info("Exiting " + self.name)
    
    def create_customers(self):
        odoo = Odoo(self.conf['odoo'])
        odoo.connect()
        model = odoo.env[self.model_name]
        customers = self.customers
        batches = tools.batcher(customers,self.batch_size)
        for counter in batches.keys():
            _logger.debug("Running Batch no : " + str(counter+1))
            partial = customers[batches[counter][0]:batches[counter][1]]
            ids = self.model.create(partial)

class Vendor(Customer):

    def __init__(self,conf):
        self.conf = conf

    def create(self,values,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        if not values or len(values) < 1:
            return
        for vendor in values:
            vendor['supplier'] = True
            vendor['is_company'] = True
            model = odoo.env[self._name]
            ids = model.create(values)
            ids.sort()
            return ids

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
