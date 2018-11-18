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

def main():
    print("Hello from main module")
    
def updateSaleOrders(sb):
    so = odoo.env['sale.order']
    so_ids = so.search([('state', 'ilike', 'sale')])
    so_data = createSaleOrders(sb)
    for ord in so_ids:
        s_ord = so.browse(ord)
        if (so_data[so_data['ORDER REFERENCE'] == s_ord.name]["ORDER REFERENCE"].count() == 1):
            print("Hello")
            updateMoveLineWithLotNo(odoo, s_ord.picking_ids,
                                    sb[so_data['ORDER REFERENCE'] == s_ord.name]['ENGINE'].values[0])
        else:
            print("ERROR : NOTHING TO DO FOR" + s_ord.name)