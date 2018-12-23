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

import saboo
import sys
import logging
import threading

from saboo import Odoo
from . import Command
from .tools import login,batcher,get_thread_conf

_logger = logging.getLogger(__name__)


class OrderInventory (threading.Thread):
    def __init__(self,conf,xls):
        threading.Thread.__init__(self)
        self.xls = xls
        self.conf = conf
    def run(self):
        self.updateOrderInventory()
    
    def updateOrderInventory(self):
        odoo = login(self.conf['odoo'])    
        order = odoo.env[self.conf['model']]
        ids = self.conf['ids']
        sb = self.xls.sb
        if not odoo:
            _logger.error("Cannot connect to Odoo")
            return       
        if not ids or sb.empty:
            _logger.error("Empty ids for running the inventory update")
            return       
        for ord in ids:
            ord_id = order.browse(ord)
            if len(ord_id.order_line)>1:
                _logger.info("Order has duplicate lines"+ord_id.name)
                duplicates+=1
                return 
            _logger.info("Starting"+self.name +" - " + ord_id.name)
            record = sb[sb['ORDERNO'] == ord_id.name]
            if not record.empty:
                serial_no = (record['ENGINE']+"/"+record['CHASSIS']).values[0]
                self.updateMoveLineWithLotNo(odoo,ord_id,serial_no)
                if ord_id.picking_ids.state == 'done':
                    _logger.error("Nothing to Do For "+ ord_id.name)
                else:
                    valid = ord_id.picking_ids.button_validate()
            else: 
                _logger.error("ERROR - Invalid Order" + ord_id.name)
            _logger.info ("Finished " + self.name +" "+ ord_id.name)

    def updateMoveLineWithLotNo(self,odoo,ord, lot_name):
        spick = odoo.env['stock.picking']
        move_line = odoo.env['stock.move.line']
        lot = odoo.env['stock.production.lot']
        picking_ids = ord.picking_ids
        for pid in picking_ids:
            _logger.debug(pid.move_line_ids)
            if not pid.move_line_ids:
                _logger.debug("----NO MOVE LINE---")
                # assign lot - should exist for sale orders
                lot_id = lot.search([('name','=',lot_name)])
                if not lot_id or len(lot_id) != 1:
                    _logger.error("----ERROR NO LOT CANNOT ALLOCATE TO MOVE LINE---")
                    return
                else:    
                    move_id = move_line.create({'move_id':ord.order_line.move_ids.id,
                                                'location_id':ord.order_line.move_ids.location_id.id,
                                                'location_dest_id':ord.order_line.move_ids.location_dest_id.id,
                                                'product_id':ord.order_line.move_ids.product_id.id,
                                                'product_uom_id':1,'picking_id':ord.picking_ids.id,
                                                'lot_id':lot_id[0],'qty_done':1})
                    #print(move_id)
                    pid.move_line_ids = [move_id]
                    
            else:    
                for ml in pid.move_line_ids:
                    if not ml.lot_id:
                        #print("creating lot : " + lot_name)
                        lotId = lot.create({'name':lot_name,'product_id':ml.product_id.id})
                        #print("Lot ID : "+str(lotId))
                        ml.lot_id = lotId
                        #print(ml.lot_id)
                    if not ml.qty_done:
                        ml.qty_done=1

class PurchaseInventory(Command):
    def run(self,conf):
        thread_list = {}
        odoo = login(conf['odoo'])
        name='purchase.order'
        criteria = [('state','ilike','purchase')]
        model = odoo.env[name]
        ids = model.search(criteria) 
        batches = batcher(ids,100)
        _logger.debug(len(batches.keys()))
        if  conf['xls']:
            xls = saboo.XLS(conf['xls'])
        else:
            _logger.error("Cannot get XL values for inventory")
            return
        for counter in batches.keys():
            partial = ids[batches[counter][0]:batches[counter][1]]
            thread = OrderInventory(get_thread_conf(conf,name,0,partial),xls)
            thread_list[counter] = thread

        # Start new Threads
        for key in thread_list.keys():
            thread_list[key].start()
        for key in thread_list.keys():
            thread_list[key].join()
        _logger.info("Exiting Main Thread")

class SaleInventory(Command):
    def run(self,conf):
        thread_list = {}
        odoo = login(conf['odoo'])
        name='sale.order'
        criteria = [('state','ilike','sale')]
        model = odoo.env[name]
        ids = model.search(criteria) 
        batches = batcher(ids,100)
        _logger.debug(len(batches.keys()))
        if  conf['xls']:
            xls = saboo.XLS(conf['xls'])
        else:
            _logger.error("Cannot get XL values for inventory")
            return
        for counter in batches.keys():
            partial = ids[batches[counter][0]:batches[counter][1]]
            thread = OrderInventory(get_thread_conf(conf,name,0,partial),xls)
            thread_list[counter] = thread

        # Start new Threads
        for key in thread_list.keys():
            thread_list[key].start()
        for key in thread_list.keys():
            thread_list[key].join()
        _logger.info("Exiting Main Thread")
