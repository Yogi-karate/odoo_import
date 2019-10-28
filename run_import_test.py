
import odoo.odoo_import as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2019-10-28T09:16:07.049Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 'requestParameters': {'sourceIPAddress': '106.200.235.22'}, 'responseElements': {'x-amz-request-id': '93CD5ABD8E34C983', 'x-amz-id-2': 'ApF8dm+NICuPrH0OKBploewM2MvmT6246wl5cqh9RV/k+K3SB/fVwl7Q19gV/o4rTJKZVkR1MAs='}, 's3': {'s3SchemaVersion': '1.0', 
    	'configurationId': 'import-odoo-dev:odoo_import.handler', 
    	'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'},
    	 'arn': 'arn:aws:s3:::odoo.file.import'}, 'object': {'key': 'pricelist.xls', 'size': 209408,
    	  'eTag': 'e552b86481c00d6892f88f771ccfa19e', 'sequencer': '005DB6B1D6BCE310F8'}}}]},{})