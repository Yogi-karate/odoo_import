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
    def __init__(self, name,method,criteria):
        self.name = name
        self.criteria = criteria
        self.method = method

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
        _logger.debug("Number of orders to confirm : " + str(len(ids)))
        odoo.run(name,self.method,ids)

class Xls(Command):
    command = 'xls'
    def run(self,conf):
        if  conf['xls']:
            _logger.info("Deleting models in order before staring import process")
            odoo = login(conf['odoo'])
            odoo.deleteModels(['purchase.order','sale.order','vendor','customer','vehicle','product.template','product.attribute'])
            _logger.info(" Finished Deleting models")
            xls = saboo.XLS(conf)
            _logger.debug("The xl file read in is "+ str(xls.sb['ORDERNO'].count()))
            xls.execute()  

class SaleConfirm(Command):
    def run(self,conf):
        name='sale.order'
        criteria = [('state','ilike','draft')]
        order_confirm = OrderConfirm(name,'action_multi_confirm',criteria)
        order_confirm.confirm(conf)

class PurchaseConfirm(Command):
    def run(self,conf):
        name='purchase.order'
        criteria = [('state','ilike','draft')]
        order_confirm = OrderConfirm(name,'button_confirm',criteria)
        order_confirm.confirm(conf)

