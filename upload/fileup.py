import os
# import magic
import urllib.request
from .app import app
from flask import Flask, flash, request, redirect, render_template,jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging
from .s3 import S3Upload as s3

ALLOWED_EXTENSIONS = set(['xls', 'csv', 'xlsx'])
cors = CORS(app)
_logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('fupload.html')

@app.route('/pricelist', methods=['POST'])
def async_upload_pricelist():
    _logger.debug(request.files)
    _logger.debug(dict(request.headers))

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
            _logger.debug("the ODOO host to use is %s",app.config['odoo']['server_name'])
            body = request.form.to_dict()
            filename = secure_filename(file.filename)
            s3_object = s3(app.config)
            body.update({'job_type':'pricelist'})
            s3_object.upload_excel(file,body)
            return jsonify({'status':'success','message':'uploaded to s3 !!! '})
        except Exception as ex:
            _logger.exception(ex)
            return jsonify({"error":"ex"})
    else:
        flash('Allowed file types are xls,xlsx,csv')
        return jsonify({'status':'error','message':'invalid request'})

@app.route('/sale', methods=['POST'])
def async_upload_sale():
    _logger.debug(request.files)
    _logger.debug(dict(request.headers))

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
            _logger.debug("the ODOO host to use is %s",app.config['odoo']['server_name'])
            body = request.form.to_dict()
            filename = secure_filename(file.filename)
            s3_object = s3(app.config)
            body.update({'job_type':'sale'})
            s3_object.upload_excel(file,body)
            return jsonify({'status':'success','message':'uploaded to s3 !!! '})
        except Exception as ex:
            _logger.exception(ex)
            return jsonify({"error":"ex"})
    else:
        flash('Allowed file types are xls,xlsx,csv')
        return jsonify({'status':'error','message':'invalid request'})

