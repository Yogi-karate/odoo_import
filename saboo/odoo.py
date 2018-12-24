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
import odoorpc as rpc
import saboo.tools as tools

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
                if len(ids) > 3000:
                    _logger.info("Number of Models to be deletedis high - running in batches - Hang on ....")
                    batches = tools.batcher(ids,3000)
                    _logger.debug(len(batches.keys()))
                    _logger.info("Number of Models to be deleted is high - running in batches - Hang on .... batch size is 2000")
                    for counter in batches.keys():
                        partial = ids[batches[counter][0]:batches[counter][1]]
                        if _name == 'purchase.order':
                            odoo.execute_kw(name,'button_cancel',[partial])
                        odoo.execute_kw(_name,'unlink',[partial])
                else:   
                    if _name == 'purchase.order':
                        odoo.execute_kw(name,'button_cancel',[ids])
                    odoo.execute_kw(_name,'unlink',[ids])

    def initialize(self):
        _logger.debug("Initializing Odoo instance")
        try:
            self.connect()
        except Exception:
            _logger.error("Invalid Odoo config")
            return
        _logger.info("Deleting models in order before staring import process")
        self.deleteModels(['purchase.order','sale.order','vendor','customer','product.template','product.attribute'])
        _logger.info(" Finished Deleting models")


    