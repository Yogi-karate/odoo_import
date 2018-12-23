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
import pandas
import saboo
import sys
import logging
import threading

from saboo import Odoo
from . import Command
from .tools import login,batcher,get_thread_conf

_logger = logging.getLogger(__name__)

class OrderConfirm():
    def __init__(self, name,criteria):
        self.name = name
        self.criteria = criteria

    def confirm(self,conf):
        # Create new threads
        thread_list = {}
        odoo = login(conf['odoo'])
        if not odoo:
            _logger.error("Cannot connect to odoo instance")
            return
        name=self.name
        criteria = self.criteria
        model = odoo.env[name]
        ids = model.search(criteria) 
        batches = batcher(ids,100)
        _logger.debug(len(batches.keys()))
        for counter in batches.keys():
            _logger.debug(len(ids[batches[counter][0]:batches[counter][1]]))
            partial = ids[batches[counter][0]:batches[counter][1]]
            thread = Order(get_thread_conf(conf,name,counter,partial))
            thread_list[counter] = thread
        # Start new Threads
        for key in thread_list.keys():
            thread_list[key].start()
        for key in thread_list.keys():
            thread_list[key].join()
        _logger.info("Exiting Main Thread")

class Order (threading.Thread):
    def __init__(self, conf):
        threading.Thread.__init__(self,None,conf['id'],conf['name'],conf)
        self.conf = conf
        self.threadID = conf['id']
        self.name = conf['name']  
    def run(self):
        _logger.info("Starting " + self.name)
        self.approve_order()
        _logger.info("Exiting " + self.name)
    
    def approve_order(self):
        conf = self.conf
        odoo = login(conf['odoo'])
        ids = conf['ids']
        #model = odoo.env[self.name]
        _logger.info("Starting batch : "+str(self.threadID))
        for counter in range(len(ids)):
            ret_val = odoo.execute_kw(conf['model'],conf['action'],[[ids[counter]]])
            _logger.debug("done with id"+str(ret_val))
        _logger.info("-------Ending batch : "+str(self.threadID)+"------")  
        
class Xls(Command):
    command = 'xls'
    def run(self,conf):
        if  conf['xls']:
            xls = saboo.XLS(conf)
            _logger.debug("The xl file read in is "+ str(xls.sb['ORDERNO'].count()))
            xls.execute()  

class SaleConfirm(Command):
    def run(self,conf):
        name='sale.order'
        criteria = [('state','ilike','draft')]
        order_confirm = OrderConfirm(name,criteria)
        order_confirm.confirm(conf)

class PurchaseConfirm(Command):
    def run(self,conf):
        name='purchase.order'
        criteria = [('state','ilike','draft')]
        order_confirm = OrderConfirm(name,criteria)
        order_confirm.confirm(conf)

