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

class User(Module):
	
	_name = 'res.users'
	ids = []
	def __init__(self,conf):
		if not conf['attributes'] or not conf['odoo']:
			raise Exception("Cannot create attributes")
		self.conf = conf
	
	def user_change_company(self,company_id):
		odoo = tools.login(self.conf['odoo'])
		current_company = odoo.env.user.company_id
		print("The copany values are ",company_id,current_company,current_company.id)
		if current_company.id != company_id:
			odoo.env.user.company_id = company_id
			_logger.warn("Changing Users comapny - execute before any ORM -- new company %s",odoo.env.user.company_id.name)
		else:
			_logger.info("Not Changing Users company , user belongs to %s",current_company.name)
	def create(self,customers,odoo):
	   pass

	def write(self,path):
		pass

	@property
	def get_field_list(self):
		return self._field_list
