
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 
        'awsRegion': 'ap-south-1', 'eventTime': '2019-11-06T11:13:17.715Z', 
        'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROA4JVB346XYSC4MMYGN:file-upload-dev'},
         'requestParameters': {'sourceIPAddress': '13.126.148.170'}, 
         'responseElements': {'x-amz-request-id': 'BEB4C7A14723349C', 'x-amz-id-2': 'NFiKjgmZ3lG9IUzD2wFU8hT0lB4r03WLEiO+ZmY7PDEo5g+mlZXKVM1dtJRg/gmWvYRJ3VICgBk='}, 
         's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.handler.handler', 
         'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 
         'arn': 'arn:aws:s3:::odoo.file.import'}, 'object': {'key': 'pricelist_5dc2aacc6deeb2001192a8b0.xls',
          'size': 174260, 'eTag': 'd62f5fa69fba8f94e97e87252108aba1', 'sequencer': '005DC2AACDA858FCCE'}}}]},{})