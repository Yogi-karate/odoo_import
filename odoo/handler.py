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
			try:
				s3_client = boto3.client('s3')
				s3_response_object = s3_client.get_object(Bucket=bucket_name, Key=file_name)
				object_content = s3_response_object['Body'].read()
				obj_data = s3_response_object['Metadata']
				_logger.debug("******* s3 object**** %s",obj_data)
				if not 'joblogid' in obj_data or not 'job_type' in obj_data:
					_logger.error("Error in metadata %s",obj_data)
					return {'message':"Error -- Could not find MetaData in file"}
				else:
					if obj_data['job_type'] == 'pricelist':
						result = odoo(config).import_pricelist(object_content,obj_data)
					if obj_data['job_type'] =='sale':
						result = odoo(config).import_sale_data(object_content,obj_data)
			except Exception as e:
				_logger.error("Exception in import process",e)
				return {'error':'Could Not Load file from S3'}
			_logger.info("The result from Import job execution %s",result)
		else:
			print("-----Unable to process Event-----")