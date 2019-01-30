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

__author__ = 'Rammohan Tangirala'
__email__ = 'ram.tangirala@gmail.com'
__licence__ = 'LGPL v3'
__version__ = '0.0.1'

from .module import Module
from .field import Field
from .purchase_order import PurchaseOrder
from .sale_order import SaleOrder
from .product_attributes import ProductAttributes
from .product import ProductTemplate
from .product import ProductProduct
from .customer import Customer,Vendor,Lead
from .vehicle import Vehicle

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
