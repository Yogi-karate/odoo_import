import logging
import boto3
import json
import saboo
import io

_logger = logging.getLogger(__name__)

class OdooImport(object):

	def __init__(self,conf):
		self.conf = conf

	def import_pricelist(self,bucket_name,file_name):
		_logger.info("import bucket %s",bucket_name)
		_logger.info("import file %s",file_name)
		if file_name and bucket_name:
			try:
				s3_client = boto3.client('s3')
				s3_response_object = s3_client.get_object(Bucket=bucket_name, Key=file_name)
				object_content = s3_response_object['Body'].read()
				obj_data = s3_response_object['Metadata']
				_logger.debug("******* s3 object****",obj_data)
				if not 'joblogid' in obj_data or not 'name' in obj_data:
					_logger.error("Error in metadata %s",obj_data)
					return {'message':"Error -- Could not find MetaData in file"}
				else:
					saboo.client._init_odoo(self.conf)
					saboo.client._init_odoo(self.conf)
					xls = saboo.PricelistXLS(self.conf)
					return xls.handle_request(io.BytesIO(object_content),obj_data['name'],obj_data['company'],obj_data['joblogid'])
			except Exception as e:
				_logger.error("Exception in import process",e)
				return {'error':'Could Not Load file from S3'}


