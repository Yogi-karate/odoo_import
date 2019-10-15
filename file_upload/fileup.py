import os
# import magic
import urllib.request
from .app import app
from flask import Flask, flash, request, redirect, render_template,jsonify
from werkzeug.utils import secure_filename
import saboo
import saboo.tools as tools
from flask_cors import CORS

ALLOWED_EXTENSIONS = set(['xls', 'csv', 'xlsx'])
cors = CORS(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('fupload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("appcon",app.config['odoo_conf'])
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return jsonify({"error":"No file part"})
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        try:
            print("sample---------",request.form)
            body = request.form
            filename = secure_filename(file.filename)
            saboo.client._init_odoo(app.config['odoo_conf'])
            xls = saboo.PricelistXLS(app.config['odoo_conf'])
            return jsonify(xls.handle_request(request.files.get('file'), body['name'], body['company']))
        except Exception as ex:
            print(str(ex))
            return jsonify({"error":"ex"})
       
    else:
        flash('Allowed file types are xls,xlsx,csv')
        return redirect(request.url)
        
@app.route('/getlead', methods=['GET'])
def getCrmLead():
    name = 'crm.lead'
    print("1----------------------",name)
    client = saboo.client
    print("2----------------------",client)
    client.conf = client._parse_config(['odoo-import.bin', '-c', 'import.conf'])
    print("3----------------------",client.conf)
    client._init_odoo(client.conf)
    odoo = saboo.tools.login(client.conf)
    print("4----------------------",odoo)
    crmLeads = odoo.env[name]
    ids = crmLeads.search([], limit =100)
    response = {}
    for id in ids:
	    lead = crmLeads.browse(id)
	   # print(lead.name)
	   # print(lead.partner_name)
	    response[id] = {"name":lead.name,"customer":lead.partner_name}
    return response
