import os
# import magic
import urllib.request
from .app import app
from flask import Flask, flash, request, redirect, render_template,jsonify
from werkzeug.utils import secure_filename
import saboo
import saboo.tools as tools
from flask_cors import CORS
import logging

ALLOWED_EXTENSIONS = set(['xls', 'csv', 'xlsx'])
cors = CORS(app)
_logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('fupload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print(app.config['odoo_conf'])
    print(request.files)
    print(dict(request.headers))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return jsonify({'status':'error','message':'no files in request'})
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        try:
            print("sample---------",request.form)
            print("the ODOO host to use is ",app.config['odoo_conf']['odoo']['server_name'])
            body = request.form
            filename = secure_filename(file.filename)
            saboo.client._init_odoo(app.config['odoo_conf'])
            saboo.client._init_logging(app.config['odoo_conf']['Logging'])
            xls = saboo.PricelistXLS(app.config['odoo_conf'])
            if body and 'name' in body:
                return jsonify(xls.handle_request(request.files.get('file'), body['name'], body['company'], body['jobLogID']))
            else:
                return jsonify(xls.handle_request(request.files.get('file')))
        except Exception as ex:
            _logger.exception(ex)
            return jsonify({"error":"ex"})
    else:
        flash('Allowed file types are xls,xlsx,csv')
        return jsonify({'status':'error','message':'invalid request'})
 
@app.route('/uploadSaleData', methods=['POST'])
def upload_sale_data_file():
    print(app.config['odoo_conf'])
    print(request.files)
    print(dict(request.headers))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return jsonify({'status':'error','message':'no files in request'})
    file = request.files['file']
    if file.filename == '':
        flash('No file selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        try:
            body = request.form
            filename = secure_filename(file.filename)
            saboo.client._init_odoo(app.config['odoo_conf'])
            saboo.client._init_logging(app.config['odoo_conf']['Logging'])
            xls = saboo.XLS(app.config['odoo_conf'])
            if body and 'name' in body:
                return jsonify(xls.handle_request(request.files.get('file'), body['company'], body['jobLogID']))
            else:
                return jsonify(xls.handle_request(request.files.get('file')))
        except Exception as ex:
            _logger.exception(ex)
            return jsonify({"error":"ex"})
    else:
        flash('Allowed file types are xls,xlsx,csv')
        return jsonify({'status':'error','message':'invalid request'})

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
