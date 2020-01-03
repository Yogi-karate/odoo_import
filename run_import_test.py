
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2019-12-18T10:14:14.318Z',
    	'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROA4JVB346XYSC4MMYGN:file-upload-dev'}, 
    	'requestParameters': {'sourceIPAddress': '13.232.155.239'}, 'responseElements': {'x-amz-request-id': '1E0B26FA2D52DC28', 
    	'x-amz-id-2': 'jUAgNQLBtTa139HMjjGlatWiZItKFbjNA0gnPWeact0FeJKSpJJVmWUYnhoPFectpvJKigoxGro='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.handler.handler',
    	 'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 'arn': 'arn:aws:s3:::odoo.file.import'}, 'object': {'key': 'sale_5df9fbf5d5280c001001fa52.xls', 
    	 'size': 320043, 'eTag': '9ff38c93b8780e53338bf2da394946c0', 'sequencer': '005DF9FBF635B1485F'}}}]},{})