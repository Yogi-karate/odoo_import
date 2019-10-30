import logging
import boto3
from botocore.exceptions import ClientError

_logger = logging.getLogger(__name__)


class S3Upload(object):
	
	def __init__(self,conf):
		#initialize boto s3 for uploads
		_logger.debug("Welcome to S3 upload")
		self.conf = conf
		if 's3' in self.conf:
			bucket_name = self.conf['s3']['bucket_name']
			print("********Bucket Name ****** !!!",bucket_name)
			self.bucket_name = bucket_name
		else:
			self.bucket_name = 'pricelist.create'

	def upload_excel(self,file,data):
		return self.upload_file(file,self.bucket_name,data)


	def upload_file(self,file, bucket,data):
	# Upload the file
		s3_client = boto3.client('s3')
		try:
			if 'jobLogID' in data and 'job_type' in data:
				filename = data['job_type']+'_'+data['jobLogID']+'.xls'
				response = s3_client.upload_fileobj(file, bucket,filename,ExtraArgs={"Metadata":data})
			else:
				print("error in data")
				return False
		except ClientError as e:
			logging.error(e)
			return False
		return True