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
import argparse
import configparser

from saboo import Odoo

conf = {}
_logger = logging.getLogger('saboo')
config = configparser.ConfigParser()
commands = {}

class CommandType(type):
    def __init__(cls, name, bases, attrs):
        super(CommandType, cls).__init__(name, bases, attrs)
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls

# Base Command Class Definition
Command = CommandType('Command', (object,), {'run': lambda self, args: None})

def main():
    conf = _parse_config()
    if conf: 
            _init_logging(conf['Logging'])
    else:
        raise Exception("Invalid Configuration")
    for command in _parse_commands():
        _logger.debug("The command to execute is "+command)
        o = commands[command]()
        _logger.debug("The command to execute is "+str(o))
        o.run(conf)
    _logger.debug("The modules are "+ conf['Modules']['name'])  

          
def _parse_commands():
    commands = []
    # check if args has 
    command_args = sys.argv[3:]
    if len(command_args) and command_args[0] and command_args[0].startswith('--'):
        _logger.debug("the command is "+command_args[0])
        commands.append('xls')
    else:
        commands.append('xls')
        _logger.info("No command given - so executing default xls import command" + str(commands))
    return commands

def _parse_config():
    parser = argparse.ArgumentParser(description='Odoo Import Process')
    parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args,other_args = parser.parse_known_args()
    if args.conf_file:
        config.read([args.conf_file])
        conf = dict(config.items())
        for key in conf:
            print(key)
        return conf    
    else:
        return False

def _init_logging(conf):
    default_format = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')
    if conf['level']:
        _logger.setLevel(conf['level'])
    if conf['handler'] and (conf['handler'] in ['file']):
        print("Hello")
        handler = logging.FileHandler(conf['logfile'])
    std_handler = logging.StreamHandler()
    handler.setFormatter(default_format)
    std_handler.setFormatter(default_format)
    _logger.addHandler(handler) 
    _logger.addHandler(std_handler)    
    _logger.info("Say something")


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

def updateOrders(model,state):
    Order = odoo.env[model]
    ids = Order.search([('state','ilike',state)])
    print(ids)
    for po in Order.browse(ids):
        print(po.name)
        print(po.picking_ids)
        record = sb[sb['ORDERNO'] == po.name]
        if not record.empty:
            print((record['ENGINE']+"/"+record['CHASSIS']).values[0])
            print(po.picking_ids.show_lots_text)
            #updateMoveLineWithLotNo(po.picking_ids,(record['ENGINE']+"/"+record['CHASSIS']).values[0])
            print(po.picking_ids.state)
            if po.picking_ids.state == 'done':
                print("Nothing to Do ")
            else:
                print("Validating Stock Pick")
                valid = po.picking_ids.button_validate()
                print(valid)
        else: 
            print("ERROR - Invalid Order" + po.name)

def batcher(ids,size):
    batch = {}
    start = 0
    end = size
    count = int(len(ids)/size)
    print(count)
    for idx in range(count):
        batch[idx] = [start,end]
        if(idx == count-1 and len(ids)%size > 0):
            batch[idx+1] = [end,len(ids)] 
        start = end
        end = end + size
    return batch 
