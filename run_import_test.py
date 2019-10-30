
import odoo.handler as odoo

if __name__ == "__main__":
    odoo.handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 
        'awsRegion': 'ap-south-1', 'eventTime': '2019-10-30T14:16:17.283Z', 
        'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A3N7R96ZNDZXWK'}, 
        'requestParameters': {'sourceIPAddress': '124.123.81.249'}, 'responseElements': {'x-amz-request-id': '388D1EC0CC09A5F9', 
        'x-amz-id-2': 'QUkAkL9Dr2iKKOtqk3cNDuVU6/oGx8jNTG5ohRW/vnZcRf9u+jv28rt+HGgHREmltydYyeG+g/g='}, 
        's3': {'s3SchemaVersion': '1.0', 'configurationId': 'import-odoo-dev:odoo.handler.handler',
         'bucket': {'name': 'odoo.file.import', 'ownerIdentity': {'principalId': 'A3N7R96ZNDZXWK'},
          'arn': 'arn:aws:s3:::odoo.file.import'}, 'object': {'key': 'sale_xzs1234.xls', 'size': 363962, 'eTag': 'b16e019e5747b9e6350ac675ae1096a8',
     'sequencer': '005DB99B310216DAEC'}}}]},{})