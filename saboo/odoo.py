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

import odoorpc as rpc


class Odoo(rpc.ODOO):

    def __init__(self, odoo_server='52.66.150.193', port=8069):
        super(Odoo,self).__init__(odoo_server,port=port)


    def approvePO(self, state):
        Order = self.env['purchase.order']
        ids = Order.search([('state', 'ilike', state)])
        for ord in ids:
            for po in Order.browse(ord):
                print("Approving Order: " + po.name)
                po.button_approve()

    def approveSaleOrder(self, state):
        Order = self.env['sale.order']
        ids = Order.search([('state', 'ilike', state)])
        for ord in ids:
            s_ord = order.browse(ord)
            print("Approving Order: " + s_ord.name)
            s_ord.action_confirm()


    def updateMoveLineWithLotNo(self, picking_ids, lot_name):
        spick = self.env['stock.picking']
        move_line = self.env['stock.move.line']
        lot = self.env['stock.production.lot']
        for pid in picking_ids:
            print(pid.name)
            print(pid.move_line_ids)
            for ml in pid.move_line_ids:
                print(ml.id)
                print(ml.qty_done)
                print(ml.lot_id)
                ml.lot_id.name = lot_name
