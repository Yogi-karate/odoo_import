import logging
import conf
import boto3
import json
import saboo
import io


_logger = logging.getLogger(__name__)
config = conf.init()

# Lambda Handler function
def handler(event,context):
	print("the event is ",event)
	if 'Records' in event and event['Records'][0]:
		s3_vals = event['Records'][0]['s3']
		if s3_vals:
			print(s3_vals['bucket']['name'])
			print(s3_vals['object']['key'])
			bucket_name = s3_vals['bucket']['name']
			file_name = s3_vals['object']['key']
			result = OdooImport(config).import_pricelist(bucket_name,file_name)
			_logger.info("The result from Import job execution",result)
		else:
			print("-----Unable to process Event-----")


class OdooImport(object):

	def __init__(self,conf):
		self.conf = conf

	def import_pricelist(self,bucket_name,file_name):
		_logger.debug("import bucket %s",bucket_name)
		_logger.debug("import file %s",file_name)
		if file_name and bucket_name:
			try:
				s3_client = boto3.client('s3')
				s3_response_object = s3_client.get_object(Bucket=bucket_name, Key=file_name)
				object_content = s3_response_object['Body'].read()
				obj_data = s3_response_object['Metadata']
				print("******* s3 object****",obj_data)
				if not 'job_id' in obj_data or not 'name' in obj_data:
					return {'message':"Error -- Could not find MetaData in file"}
				else:
					saboo.client._init_odoo(self.conf)
					xls = saboo.PricelistXLS(self.conf)
					return xls.handle_request(io.BytesIO(object_content),obj_data['name'],obj_data['job_id'])
			except Exception as e:
				print(e)
				return {'error':'Could Not Load file from S3'}