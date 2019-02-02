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
from .field import Field
import saboo
from .module import Module
import saboo.tools as tools


class PurchaseOrder(Module):
    
    _name = 'purchase.order'
    _field_list = None
    po_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference',
					'Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID',
					'Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID',
					'Vendor','Order Lines/Product','Status']

    def __init__(self,conf):
        if not conf['attributes'] or not conf['odoo']:
            raise Exception("Cannot create attributes")
        self.conf = conf

    def create(self,purchase_list,odoo):
        if not odoo:
            odoo = tools.login(self.conf['odoo'])
        self.model = odoo.env[self._name]
        for po in purchase_list:
            po['order_line'] = self.create_order_line(po)
        odoo.run(self._name,'create',purchase_list)

    def create_order_line(self,po):
        order_line = {'product_qty':1,'product_uom':1}
        order_line['date_planned'] = po['date_order']
        order_line['product_id'] = po['product_id']
        order_line['name'] = po['line_name']
        order_line['price_unit'] = po['price_unit']
        order_line['taxes_id'] = self.create_tax_line(po)
        return [[0,'_',order_line]]

    def create_tax_line(self,line_dict):
        # REDO LATER ---- need to fetch the right tax id 
        return [[6, False, [45,46]]]

    def write(self,path):
        pass

    def delete(self):
        return True

    @property
    def get_field_list(self):
        return self._field_list



