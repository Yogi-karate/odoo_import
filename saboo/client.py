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
from . import config as globals

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
    print("The args = " + str(sys.argv))
    conf = _parse_config(sys.argv)
    if conf: 
            _init_logging(conf['Logging'])
            _init_odoo(conf)
    else:
        raise Exception("Invalid Configuration")
    try:    
        for command in _parse_commands():
            _logger.debug("The command to execute is "+command)
            o = commands[command]()
            _logger.debug("The command to execute is "+str(o))
            o.run(conf)
        _logger.debug("The modules are "+ conf['Modules']['name'])  
    except Exception as ex:
        _logger.fatal("Error executing command")
        _logger.exception(ex)

def _parse_commands():
    commands = []
    # check if args has 
    command_args = sys.argv[3:]
    if len(command_args) and command_args[0] and command_args[0].startswith('--'):
        _logger.debug("the command is "+command_args[0][2:])
        commands.append(command_args[0][2:])

    else:
        commands.append('xls')
        _logger.info("No command given - so executing default xls import command" + str(commands))
    return commands

def update_config(section,name,value):
    if section and name and value:
        config.set(section,name,value) 
        conf = dict(config.items())

def _parse_config(sysconf):
    parser = argparse.ArgumentParser(description='Odoo Import Process')
    parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args,other_args = parser.parse_known_args(sysconf)
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

    if conf['handler'] in conf and conf['handler']['logfile']:
        handler = logging.FileHandler(conf['logfile'])
        handler.setFormatter(default_format)
        _logger.addHandler(handler) 
    std_handler = logging.StreamHandler()
    std_handler.setFormatter(default_format)
    _logger.addHandler(std_handler)    
    _logger.info("Say something")

def _init_odoo(conf):
    odoo = Odoo(conf['odoo'])
    odoo.initialize()
    globals.odoo_conf['instance'] = odoo
