import logging
import conf
import boto3
import json
import io
from . import OdooImport as odoo

_logger = logging.getLogger(__name__)
config = conf.init()

# Lambda Handler function
def handler(event,context):
	_logger.debug("the event is ",event)
	if 'Records' in event and event['Records'][0]:
		s3_vals = event['Records'][0]['s3']
		if s3_vals:
			_logger.debug(s3_vals['bucket']['name'])
			_logger.debug(s3_vals['object']['key'])
			bucket_name = s3_vals['bucket']['name']
			file_name = s3_vals['object']['key']
			result = odoo(config).import_pricelist(bucket_name,file_name)
			_logger.info("The result from Import job execution %s",result)
		else:
			print("-----Unable to process Event-----")