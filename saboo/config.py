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

_logger = logging.getLogger(__name__)

class Config(object):
    conf = {}
    


def batcher(ids,size):
    batch = {}
    start = 0
    end = size
    count = int(len(ids)/size)
    _logger.debug(count)
    for idx in range(count):
        batch[idx] = [start,end]
        if(idx == count-1 and len(ids)%size > 0):
            batch[idx+1] = [end,len(ids)] 
        start = end
        end = end + size
    return batch

def login(conf):
    if odoo:
        return odoo
    else:
        _logger.warning("Recreating Odoo instance")
        odoo = saboo.Odoo(conf)
        return odoo

def get_thread_conf(conf,name,counter,ids):
    thread_conf = {}
    thread_conf['id'] = counter
    thread_conf['name'] = name+str(counter)
    thread_conf['model'] = name
    thread_conf['ids'] = ids
    if name.startswith('purchase'):
        thread_conf['action'] = 'button_confirm'
    else:
        thread_conf['action'] = 'action_confirm'
    thread_conf['model'] = name
    thread_conf['odoo'] = conf['odoo']
    return thread_conf