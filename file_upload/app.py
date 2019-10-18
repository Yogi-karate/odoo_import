import os
from flask import Flask
import saboo
#from flask_cors import CORS

UPLOAD_FOLDER = '/Users/tramm/Downloads'
app = Flask(__name__)
#cors = CORS(app, resources={r"/": {"origins": "*"}})
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
print(os.environ.get('FILEUP_CONFIG'))
if os.environ.get('FILEUP_CONFIG'):
	conf = os.environ.get('FILEUP_CONFIG')
	config_filename = 'import_'+conf+'.conf'
	print("******* Reading Config from ",config_filename," *******")
	app.config['odoo_conf'] = saboo.client._parse_config(['odoo-import.bin', '-c', 'import_'+conf+'.conf'])	 
else:
	app.config['odoo_conf'] = saboo.client._parse_config(['odoo-import.bin', '-c', 'import.conf'])