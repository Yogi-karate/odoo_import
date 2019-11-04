
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3',
     'awsRegion': 'ap-south-1', 'eventTime': '2019-11-04T08:27:00.989Z', 
     'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AROA4JVB346XYSC4MMYGN:file-upload-dev'},
      'requestParameters': {'sourceIPAddress': '13.127.117.133'}, 
      'responseElements': {'x-amz-request-id': '635CD47CBED7BE90', 'x-amz-id-2': 'x1W9temyxP/rf4AYmaHoJKLuJqwDoC378TMKvPiRESu5sJRFmiILkKsucWT1BSzrLmFd90NSC5M='},
       's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.handler.handler',
        'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 
        'arn': 'arn:aws:s3:::odoo.file.import'}, 'object': {'key': 'sale_s1x1234.xls', 'size': 364150, 
    	'eTag': 'a50abcdbda42708c1509508fcfd80b26', 'sequencer': '005DBFE0D4E06B7F59'}}}]},{})