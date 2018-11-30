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


from saboo import Odoo
from . import Command
_logger = logging.getLogger(__name__)

class Xls(Command):
    command = 'xls'
    def run(self,conf):
        if  conf['xls']:
            xls = saboo.XLS(conf['xls'])
            _logger.debug("The xl file read in is "+ str(xls.sb['ORDERNO'].count()))
            xls.execute()  

class SaleConfirm(Command):
    def run(self,conf):
        pass

class PurchaseConfirm(Command):
    def run(self,conf):
        pass

class PurchaseInventory(Command):
    def run(self,conf):
        pass

class SaleInventory(Command):
    def run(self,conf):
        pass