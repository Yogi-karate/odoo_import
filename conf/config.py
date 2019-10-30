import os
import logging
import logging.config
import argparse
from configparser import ConfigParser

config = ConfigParser()

def _parse_config(config_file):
	if config_file:
		print("******* Reading Config from ",config_file," *******")
		try:
			config.read([config_file])
			conf = dict(config.items())
			for key in conf:
				print(key)
			return conf    
		except Exception as ex:
			print("Error Occured in loading configuration !!!!!",ex)
		

def _init_logging():
	logging.config.fileConfig(config)
	rooter = logging.getLogger()
	print(rooter)
	rooter.debug("Completed Logging Setup!!!!!!",)
	#("Completed Logging Setup")

def init():
	print(os.environ.get('FILEUP_CONFIG'))
	if os.environ.get('FILEUP_CONFIG'):
		conf = os.environ.get('FILEUP_CONFIG')
		config_filename = 'import_'+conf+'.conf'
	else:
		config_filename = 'import.conf'
	conf = _parse_config(config_filename)
	_init_logging()
	return conf