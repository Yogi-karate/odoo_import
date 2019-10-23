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
			self.root = 'http://localhost:8000/api/v1/public/'

	
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

	def finishJob(self):
		# finish the pricelist job
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


