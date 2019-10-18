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
if os.environ.get('FILEUP_CONFIG') == 'dev':
	app.config['odoo_conf'] = saboo.client._parse_config(['odoo-import.bin', '-c', 'import_dev.conf'])	 
else:
	app.config['odoo_conf'] = saboo.client._parse_config(['odoo-import.bin', '-c', 'import.conf'])