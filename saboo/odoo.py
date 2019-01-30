# -*- coding: UTF-8 -*-
##############################################################################
#
#    Saboo Import
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
"""
This module contains Loading of Saboo specific xl sheets for odoo import
"""

import logging
import threading

import odoorpc as rpc
from . import tools

_logger = logging.getLogger(__name__)

class Odoo(rpc.ODOO):

    def __init__(self, conf):
        if not conf or not conf['server_name'] or not conf['port']:
            _logger.error("Invalid Configuration")
            raise Exception(" Cannot connect to Odoo instance")
        self.conf = conf
        odoo_server = conf['server_name']
        port = conf['port']
        timeout = conf['timeout']
        super(Odoo,self).__init__(odoo_server,port=port,timeout=timeout)

    def connect(self):
        conf = self.conf
        username = conf['user_name']
        password = conf['password']
        database = conf['database']
        self.login(database,username,password)

    def deleteModels(self,names):
        # Naive implementation to delete all in one go - change later
        odoo = self
        if not odoo:
            _logger.error("Cannot delete objects - invalid config")
        for name in names:    
            _logger.info("Deleting models of "+ name)
            if name in ['customer']:
                _name = 'res.partner'
                criteria = [('customer','=',True)]
            elif name in ['vendor']:
                _name = 'res.partner'
                criteria = [('supplier','=',True)]
            else:    
                _name = name
                criteria = []
            model = odoo.env[_name]
            ids = model.search(criteria)
            if len(ids) < 1:
                _logger.info("No Records in DB for " + name)
            else:    
                _logger.info("Number of Models to be deleted - "+str(len(ids)))
                if _name == 'purchase.order':
                    self.run(name,'button_cancel',ids)
                if _name in ['stock.picking','sale.order']:
                    self.run(name,'action_cancel',ids)
                self.run(_name,'unlink',ids)
    
    def run(self,name,method,ids):
        self.max_records = int(self.conf['max_records'])
        self.batch_size = int(self.conf['batch_size'])
        _logger.debug("The batching values are  " + str(self.max_records)+" "+str(self.batch_size))
        if len(ids) > self.max_records:
            thread_list = {}
            batches = tools.batcher(ids,self.batch_size)
            _logger.debug("Number OF Batches is "+str(len(batches.keys())))
            for counter in batches.keys():
                _logger.debug("Running Batch no : " + str(counter+1))
                partial = ids[batches[counter][0]:batches[counter][1]]
                thread = OdooThread("Thread-"+str(counter),name,method,self.conf,partial)
                thread_list[counter] = thread
            # Start new Threads
            for key in thread_list.keys():
                thread_list[key].start()
            for key in thread_list.keys():
                thread_list[key].join()
            _logger.info("Exiting Main Thread")
        else:
            _logger.info("Running Normal execute")
            self.connect()
            return self.execute_kw(name,method,[ids])

    def initialize(self):
        _logger.debug("Initializing Odoo instance")
        try:
            self.connect()
        except Exception:
            _logger.error("Invalid Odoo config")
            return

class OdooThread(threading.Thread):

    def __init__(self,thread_name,model_name,method,conf,ids):
        threading.Thread.__init__(self)
        if not method or not model_name or not ids:
            raise Exception(" Cannot run thread  - invalid configuration")
        self.conf = conf
        self.ids = ids
        self.batch_size = int(conf['max_thread_records'])
        self.name = thread_name
        self.model_name = model_name
        self.method = method

    def run(self):
        _logger.info("Starting " + self.name)
        self.process()
        _logger.info("Exiting " + self.name)
    
    def process(self):
        odoo = Odoo(self.conf)
        odoo.connect()
        model = odoo.env[self.model_name]
        ids = self.ids
        batches = tools.batcher(ids,self.batch_size)
        for counter in batches.keys():
            _logger.debug("Running "+self.name+" Batch no : " + str(counter+1))
            partial = ids[batches[counter][0]:batches[counter][1]]
            try:
                res = odoo.execute_kw(self.model_name,self.method,[partial])
            except Exception as ex:
                _logger.error("ERROR - Cannot Process the odoo method for  " + str(model))
                _logger.exception(ex)

    