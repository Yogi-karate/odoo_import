import requests
import logging

_logger = logging.getLogger(__name__)

class PriceListJobApi(object):

	def __init__(self, conf):

		self.conf = conf
		if conf.get('api'):
			self.root = conf['api']['root']
			if not self.root.endswith('/'):
				self.root = self.root + '/'
		else:
			self.root = 'http://dev.api.turnright.tech/api/v1/public'

	
	def startJob(self):
		# start the pricelist job
		if self.root:  
			url = self.root+'appVersion'
		else:
			return False
		try:
			response = requests.get(url)
			_logger.debug("the response from api is %s ",response)
			_logger.debug("the response from api is %s ",response.json())
		except HTTPError as http_err:
			_logger.error(http_err)
			return False  
		except Exception as err:
			_logger.error('Some Other error occurred:',err)  
			return False
		else:
			print('Success!')
		return True

	def finishJob(self,job_id, status):
		# finish the pricelist job
		if self.root:  
			#url = self.root+'appVersion'
			url = self.root+'/jobLog/update/'+job_id
			res = requests.post(url, json={"status":status})
			if res.ok:
				_logger.info("Update Job id Success -----------",res.json())
			else:
				_logger.error("Update Job id failed -----------") 	
			#return res.json()
		else:
			 _logger.error("Update Job id failed because of configuration issue-----------")
		# try:
		# 	res = requests.post(url, json={"status":"success"})
		# 	if res.ok:
  #   		print res.json()
		# except HTTPError as http_err:
		# 	_logger.error(http_err)
		# 	return False  
		# except Exception as err:
		# 	_logger.error('Some Other error occurred:',err)  
		# 	return False
		# else:
		# 	print('Success!')
		#return True


