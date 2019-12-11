
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2019-11-29T08:07:14.137Z', 'eventName': 'ObjectCreated:Put',
     'userIdentity': {'principalId': 'AWS:AROA4JVB346XYSC4MMYGN:file-upload-dev'}, 'requestParameters': {'sourceIPAddress': '13.232.38.235'}, 
     'responseElements': {'x-amz-request-id': '6A9DCBCBA800E49D', 'x-amz-id-2': 'GQk/aCLkYN5SYy3FIg2xzbZr0nrepW5ieLflYYm18fHM9OU8n4Ti0siUe+oJH/QL+V0VIwU4bDk='}, 
     's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.handler.handler', 'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 
     'arn': 'arn:aws:s3:::odoo.file.import'}, 
    	'object': {'key': 'sale_5de0d1b1d905dd0010e60182.xls', 'size': 320027, 'eTag': 'bd332bf95fc54949c21fbbef66e648ee', 'sequencer': '005DE0D1B20FED50F9'}}}]},{})