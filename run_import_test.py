
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 
    	'eventTime': '2019-10-29T12:36:11.717Z', 'eventName': 'ObjectCreated:Put',
    	 'userIdentity': {'principalId': 'AWS:AROA4JVB346XYSC4MMYGN:file-upload-dev'}, 
    	 'requestParameters': {'sourceIPAddress': '13.235.27.16'},
    	  'responseElements': {'x-amz-request-id': '01B5ED2132683237', 
    	  'x-amz-id-2': 'FEASGToBGVFBAwlSXtGh9WcYhv+J4X4tdHab7ZD7IjPrjLDBNj+20sHu9dBUqhdEbmfYWlWL/cE='}, 
    	  's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.odoo_import.handler',
    	   'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'},
    	    'arn': 'arn:aws:s3:::odoo.file.import'}, 
    	'object': {'key': 'pricelist_5db813e45c709d00113d0b6bcccc.xls', 'size': 209408, 'eTag': 'e552b86481c00d6892f88f771ccfa19e', 'sequencer': '005DB8323BA16FC861'}}}]},{})