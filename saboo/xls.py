# -*- coding: UTF-8 -*-
##############################################################################
#
#    Saboo Import
#    Copyright (C) 2014 Rammohan Tangirala.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
This module contains Loading of Saboo specific xl sheets for odoo import
"""
import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime

import saboo.modules as modules
import saboo.api as api
from threading import Thread

_logger = logging.getLogger(__name__)


class XLS(object):
	sb = None
	xlsx = None
	# _product_columns = {'NAME':str}
	# _customer_attribute_columns = ['CNAME','TEL']
	# _customer_columns = {'CNAME':str,'TEL':str,'ADD1':str,'CITY':str,'PCODE':str,'EMAIL':str}
	# _order_columns = {'ORDERDATE':str}
	_products = None
   # modules = {1:'attributes',2:'products',3:'purchase_orders',4:'customers',5:'sale_orders',6:'enquiries'}
	_valid = True
	_mode = 'manual'
	
	def __init__(self, conf,saboo_path='Saboo_data.xlsx',
				 sheet='Sale'):
		if conf and conf['xls'] and conf['xls']['root'] and conf['Modules']['name']:
			self.conf = conf
			self.root = conf['xls']['root']
			if not self.root.endswith('/'):
				self.root = self.root+'/'
			self.path = self.root+conf['xls']['xl_file']
			self.modules = conf['Modules']['name'].split(',')
			self.sheet = conf['xls']['sheet_name']
		else:
			_logger.error("Invalid Configuration - Cannot execute")
			raise Exception("Cannot process excel file")    
		if conf['xls'] and conf['xls']['mode'] == 'auto':
			self.xlsx = pd.ExcelFile(self.path or saboo_path)
			self.original = pd.read_excel(self.xlsx,sheet_name=None)
			self.sb = self.original
			if 'purchase_order' in self.modules:
				self.vendor_master =  pd.read_excel(self.xlsx, 'vendor')
			self.prepare()
		else:
			_logger.info("-----XLS not loaded in init------")
	

		
	
	def column_converters(self,attr):
		try:
			method_name = attr + "_columns"
			columns = getattr(self,method_name)
			print(columns)
		except Exception as ex:
			_logger.error("Invalid Conversion of columns to string dicts")
			_logger.exception(ex)
			return
		if columns:
			return {x:str for x in columns}
		else:
			raise Exception("Invalid Configuration - Cannot Convert " + attr )

	def _get_config_columns(self,section,col='columns'):
		conf = self.conf
		if not section:
			return
		vals = conf[section][col]
		if vals:
			return vals.upper().split(',')

	def get_all_columns(self):
		# need to dynamically load all fields - to do - CHANGE this !!!!
		#print(dict(self._product_columns.items()+self._attribute_columns.items()))
		all_cols = {}
		models = self.conf['xls']['column_models'].split(',')
		if not models:
			models = ['product','customer','attribute','order']
		for val in models:
			all_cols.update(self.column_converters(val))
		return all_cols
	
	@property
	def attribute_columns(self):
		return self._get_config_columns('attributes')

	@property
	def product_attribute_columns(self):
		copy = self.attribute_columns.copy()
		copy.insert(0,'NAME')
		return copy
	@property
	def product_attribute_columns_ext(self):
		copy = self.product_attribute_columns
		copy.insert(0,'External NAME')
		return copy

	@property
	def customer_attribute_columns(self):
		return self._get_config_columns('customers','mandatory_columns')
	
	@property
	def customer_columns(self):
		return self._get_config_columns('customers')

	@property
	def product_columns(self):
		return self._get_config_columns('products')
	
	@property
	def order_columns(self):
		return self._get_config_columns('orders')
			
	@property
	def products(self):
		return self._products
   
	def write(self,df,filename):
		if df is not None:
			df.to_csv(self._output_dir+filename+'.csv')
		else:
			_logger.debug("Nothing to write")

	def _validate(self):
			sb = self.sb
			self._errored = sb[sb['ORDERNO'].isna() | sb['NAME'].isna() | sb['CNAME'].isna() 
							| sb['ORDERDATE'].isna() | sb.duplicated(['ORDERNO'],False)|sb.duplicated(['ENGINE'],False)] 
			if(len(self._errored.index)>0):
				_logger.error("Sheet has " + str(len(self._errored.index))+" invalid records")
				self.sb = sb.drop(self._errored.index.values)
				# Cleaning up indexes
				self.sb.reset_index(drop=True)
				_logger.info("Total Records to be processes are " + str(len(sb.index)))
				self.write(self._errored,'errors')
			else:   
				return True

	def fillna(self):
		columns = self.get_all_columns()
		for column in columns:
			_logger.debug("The column to fillna is " + column)
			self.sb[column] = self.sb[column].str.strip()
			self.sb[column] = self.sb[column].fillna('')


	def prepare(self):
		conf = self.conf['xls']
		self._mode = self.conf['xls']['mode']
		# output_dir = self.root + conf['output_folder']
		# op = os.path.join(output_dir,conf['version'])
		# if op and not os.path.isdir(op):
		# 	os.makedirs(op)
		# _logger.debug("The outut directory is"+op) 
		self._output_dir = '/tmp'
		# self._original = self.sb.copy()
		_logger.debug("Ignore errors  in sheet - "+conf['ignore_errors'])
		if self._validate() or conf['ignore_errors'] == '1':
			self.fillna()
			_logger.debug("Setting Up Product Data from Xl File")    
			self.prepareProducts()
			_logger.debug("Setting Up Customer Data from Xl File")    
			self.prepareCustomers()
		else:
			_logger.error("Error in processing the xl file. Please fix and retry")
			self._valid = False


	def prepareProducts(self):
		
		sb = self.sb
		sb.loc[:,'External NAME'] = ""
		gp_prods = sb.groupby([sb[x].str.upper() for x in self.product_attribute_columns])
		prod_id = 0
		products = pd.DataFrame()
		for name,group in gp_prods:
			temp = pd.DataFrame()
			sb.loc[group.index.values,'External NAME'].apply(lambda row:str(prod_id))
			temp = sb.loc[group.index.values[:1]][self.product_attribute_columns_ext]
			products = pd.concat([products,temp])
			prod_id += 1
		self._products = products
		_logger.debug(self._products)

	
	def prepareCustomers(self):
		if 'customer' in self.modules:
			sb = self.sb
			sb['Customer/External ID'] = sb.index
			sb['Customer/External ID'] =sb['Customer/External ID'].apply(lambda index: "customer_template_"+str(index))
			sb.loc[:,'CDUP'] = sb.duplicated(self.customer_attribute_columns,False).values
			gp_cust = sb[sb['CDUP'] == True].groupby(self.customer_attribute_columns,sort=False)
			for name,group in gp_cust:
				group.loc[group.index.values[1:],'Customer/External ID'] = group.loc[group.index.values[:1],'Customer/External ID'].values[0]
		else:
			_logger.debug("No customer prep needed")

	
	def deduplicate(self,sb,list_cols):
		dedup = pd.DataFrame()
		for col in list_cols:
			sb[col] = sb[col].str.upper()
		dedup = sb.drop_duplicates(list_cols,keep='first')
		return dedup
	
	def getColumnDict(self,list_cols):
		d = {list_cols[i]:[] for i in range(0,len(list_cols))}
		return d 


	def handle_request(self,sheet,company_id = 1,job_id = '5db168295e1e9f00115cd74b'):
		self.sb = sheet
		self.prepare()
		return self.execute(company_id, job_id)

	def execute(self, company_id = 1,job_id = '5db168295e1e9f00115cd74b'):
		status = 'success'
		task = api.PriceListJobApi(self.conf)
		if self._valid:
			#_logger.info("Processing "+str(self.sb['ORDERNO'].count())+" Records")
			_logger.info("The modules to be executed are " + str(self.modules) + " in mode " + self._mode)
			for module in self.modules:
				try:
					# module = self.modules[key]
					method = 'create_'+module+'s'
					if self._mode is 'manual':
						method  = method+'_manual'
					_logger.info("START CREATING ---> "+module.upper())
					start = datetime.now()    
					self.write(getattr(self,method)(),module)
					finish = datetime.now() - start
					finish_time = int(finish.total_seconds()/60)
					_logger.info("END CREATING ---> "+module.upper() + " - Finished in - "+str(finish_time if finish_time >0 else finish.total_seconds()))
					status = 'success'
				except Exception as ex:
					 _logger.exception(ex)
					 status = 'error'
		else:
			_logger.error("Cannot execute with invalid data")
			status = 'error'
		task.finishJob(job_id, status)        

	def create_attributes(self):
		attributes = modules.ProductAttributes(self.conf)
		prods = self._products
		self.attribute_values = attributes.create({attribute:prods.loc[prods.duplicated(attribute)<1,attribute].sort_values().values for attribute in self.attribute_columns},None)
		_logger.info("Number of attributes created --> "+str(len(self.attribute_values)))


	def create_attributes_manual(self):
		attribs = self._products
		final = pd.DataFrame()
		for col in self.attribute_columns:
			af = pd.DataFrame()
			af['value_ids/name'] = attribs.loc[attribs.duplicated(col)<1,col].values
			af.loc[0,'name'] = col
			af.loc[0,'Type'] = "Select"
			final = pd.concat([final,af])
		return final

	def create_products(self):
		prod_templates = []
		print("UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
		print(self.products)
		gp_prods = self._products.groupby([self._products['NAME'].str.upper()])
		for name,group in gp_prods:
			template = {'name':name,'values':[(x,group[x].drop_duplicates().values) for x in self.attribute_columns]}
			prod_templates.append(template)
		product = modules.ProductTemplate(self.conf)
		template_ids = product.create(prod_templates,self.attribute_values,None)
		for index in range(len(template_ids)):
			prod_templates[index]['id'] = template_ids[index]
			self.products.loc[self.products['NAME'].str.lower() == prod_templates[index]['name'].lower(),'product_tmpl_id'] = str(template_ids[index])
		self.product_templates = prod_templates
		# update whole table with product_product id
		self.update_product_id()
	   
	
	def update_product_id(self):
		prods = self.products
		sb = self.sb
		print("*******************************************************",prods)
		print("===============================================",self._products)
		product_product = modules.ProductProduct(self.conf)
		prods['Product ID'] = product_product.create(prods.to_dict(orient='records'),self.attribute_values,self.attribute_columns,None)
		gp_prods = sb.groupby([sb[x].str.upper() for x in self.product_attribute_columns])
		for name,group in gp_prods:
			#_logger.debug(name)
			#_logger.debug(group[self.product_attribute_columns])
			self.sb.loc[group.index.values,'External NAME'] = prods.loc[group.index.values[:1],'Product ID'].values
			_logger.debug(self.sb.loc[group.index.values,'External NAME'].values)    
			
	def create_products_manual(self):
		template_cols = ['External ID','Name','Product Attributes/ Attribute Values','Product Attributes/Attribute','Type','Tracking']
		prods = self._products
		tprod = prods.T.reset_index()
		final = pd.DataFrame()
		for col in range(prods['NAME'].count()):
			sample = pd.DataFrame()
			sample['Product Attributes/Attribute'] = tprod['index'][2:].values
			sample['Product Attributes/ Attribute Values'] = tprod[col][2:].values
			sample.loc[0,'name'] = tprod.loc[tprod['index']=='External NAME',col].values[0]
			sample.loc[0,'External Id'] = "product_new_template_"+str(col)
			sample.loc[0,'Type'] = "Storable Product"
			sample.loc[0,'Tracking'] = "By Unique Serial Number"
			final=pd.concat([final,sample])
		return final

	def create_customers(self):
		cust = pd.DataFrame()
		cust[['name','mobile','street','city','zip','email','Customer/External ID']] = self.sb[['CNAME','TEL','ADD1','CITY','PCODE','EMAIL','Customer/External ID']]
		cust['street2'] = self.sb.ADD1+" "+ self.sb.ADD2
		cust['customer'] = True
		cust = self.deduplicate(cust,['name','mobile'])
		customer = modules.Customer(self.conf)
		ids = customer.create(cust.to_dict(orient='records'),None)
		_logger.debug(len(ids))
		_logger.debug(cust['name'].count())
		cust['Customer ID'] = ids
		self.update_customer_id(cust)
		self.customers = cust
	
	def update_customer_id(self,cust):
		_logger.debug("----Updating Customer ID in Table----")
		sb = self.sb
		sb.loc[sb['CDUP'] == False,'Customer/External ID'] = cust['Customer ID']
		gp_cust = sb[sb['CDUP'] == True].groupby([self.sb[x].str.upper() for x in self.customer_attribute_columns],sort=False)
		for name,group in gp_cust:
			sb.loc[group.index.values,'Customer/External ID'] = cust.loc[group.index.values[:1],'Customer ID'].values[0]
		_logger.debug(sb['Customer/External ID'][:100].values)    

	def create_customers_manual(self):
		cust = pd.DataFrame()
		cust_template = ['CUSTOMER NAME','Mobile','Phone','Email','Street','Street2','CITY','ZIP','T/R NO','Registration number','Name','Created On','ORDER NO']
		cust[['NAME','Mobile','Street','CITY','ZIP','Email','External ID']] = self.sb[['CNAME','TEL','ADD1','CITY','PCODE','EMAIL','Customer/External ID']]
		cust['Street2'] = self.sb.ADD1.astype('str')+" "+ self.sb.ADD2.astype('str')
		cust = self.deduplicate(cust,['NAME','Mobile'])
		return cust
	
	def create_vendors(self):
		_logger.debug("START CREATING VENDORS")
		if not self.vendor_master.empty:    
			_logger.info(self.vendor_master['name'].count())
			vendor = modules.Vendor(self.conf)
			self.vendor_id = vendor.create(self.vendor_master.to_dict(orient = 'records'),None)
			_logger.debug("END CREATING VENDORS")
			return self.vendor_id
		_logger.debug("END CREATING VENDORS")
		return True

		
	def create_purchase_orders(self):
		id = self.create_vendors()
		_logger.debug("The vendor id is "+str(id))
		if id:
			po_df = pd.DataFrame()
			po_df[['name','date_order','product_id','line_name','price_unit']] = self.sb[['ORDERNO','ORDERDATE','External NAME','NAME','EXSRPRICE']]
			po_df.loc[:,'partner_id'] = id[0]
			po = modules.PurchaseOrder(self.conf)
			po.create(po_df.to_dict(orient = 'records'),None)

			return

	def create_purchase_orders_manual(self):    
		po = pd.DataFrame()
		po_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference','Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID','Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID','Vendor','Order Lines/Product','Status']
		#po[['Order Date','Order Lines/Scheduled Date','Order Lines/Description','Order Lines/Product','Order Lines/Unit Price']] = sb[['ORDERDATE','ORDERDATE','NAME','NAME','BASIC']]
		po[['Order Date','Order Lines/Product/Database ID','Order Lines/Unit Price']] = self.sb[['ORDERDATE','External NAME','BASIC']]
		po[['ORDER REFERENCE','Order Lines/Scheduled Date','Order Lines/Description']] = self.sb[['ORDERNO','ORDERDATE','NAME']]
		po['Vendor'] = "Suzuki Motorcycle India Private Limited"
		po['Status'] = "purchase"
		po['Order Lines/Product Unit Of Measure/Database ID'] = "1"
		po['Order Lines/Quantity'] = "1"
		# Change to right tax value later -------
		po['Order Lines/Taxes/Database ID'] = "53"
		po['External ID'] = po.reset_index()['index'].apply(lambda index: "purchase_template_"+str(index))
		return po
	
	def create_vehicles(self):
		vehicle_df = pd.DataFrame()
		vehicle_df[['name','chassis_no','ref','registration_no','product_id']] = self.sb[['ENGINE','CHASSIS','ORDERNO','TRNO','External NAME']]
		vehicle = modules.Vehicle(self.conf)
		vehicle.create(vehicle_df.to_dict(orient = 'records'),None)
	
	def init_inventory(self):
		inventory_df = pd.DataFrame()
		inventory_df[['order_no','vehicle']] = self.sb[['ORDERNO','ENGINE']]
		return inventory_df
			
	def create_inventory(self):
		inventory_df = self.init_inventory()
		self.create_purchase_inventory(inventory_df)
		_logger.debug("Starting Sale Order Inventory")
		self.create_sale_inventory(inventory_df)

	def create_purchase_inventory(self):
		df = self.init_inventory()
		inventory = modules.Inventory(self.conf)
		inventory.confirm_purchase_orders(df.to_dict(orient = 'records'),None)

	def create_sale_inventory(self):
		df = self.init_inventory()
		inventory = modules.Inventory(self.conf)
		inventory.confirm_sale_orders(df.to_dict(orient = 'records'),None)

	def create_enquiries(self):
		return self.create_enquiries_manual()
		
	def create_enquiries_manual(self):
		pipeline = pd.DataFrame()
		pipeline[['Name','Created on','Expected Revenue','CUSTOMER/Database ID']] = self.sb[['NAME','ORDERDATE','EXSRPRICE','Customer/External ID']]
		pipeline['Notes'] = self.sb['ORDERNO'].apply(lambda ord: "Order Number : " + str(ord))
		pipeline['STAGE'] = "Won"
		pipeline = self.deduplicate(pipeline,['Notes'])
		return pipeline

	def create_sale_orders(self):
		so_df = pd.DataFrame()
		so_df[['name','date_order','product_id','line_name','price_unit','partner_id']] = self.sb[['ORDERNO','ORDERDATE','External NAME','NAME','EXSRPRICE','Customer/External ID']]
		so = modules.SaleOrder(self.conf)
		so.create(so_df.to_dict(orient = 'records'),None)
		return

	def create_sale_orders_manual(self):
		so = pd.DataFrame()
		so_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference','Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID','Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID','Vendor','Order Lines/Product','Status']
		#po[['Order Date','Order Lines/Scheduled Date','Order Lines/Description','Order Lines/Product','Order Lines/Unit Price']] = sb[['ORDERDATE','ORDERDATE','NAME','NAME','BASIC']]
		so[['Order Date','Order Lines/Product/Database ID','Order Lines/Unit Price','CUSTOMER/Database ID']] = self.sb[['ORDERDATE','External NAME','BASIC','Customer/External ID']]
		so[['ORDER REFERENCE','Order Lines/Description']] = self.sb[['ORDERNO','NAME']]
		so['Order Lines/Quantity'] = "1"
		# Change to right tax value later -------
		so['Order Lines/Taxes/Database ID'] = "25"
		so['External ID'] = so.reset_index()['index'].apply(lambda index: "sale_order_template_"+str(index))
		#so = self.deduplicate(so,['ORDER REFERENCE'])
		return so

class ProductXLS(XLS):
	  
	def _validate(self):
		sb = self.sb
		self._errored = sb[sb['NAME'].isna() | sb['VARIANT'].isna() | sb['COLOR'].isna()] 
		if(len(self._errored.index)>0):
			_logger.error("Sheet has " + str(len(self._errored.index))+" invalid records")
			self.sb = sb.drop(self._errored.index.values)
			# Cleaning up indexes
			self.sb.reset_index(drop=True)
			_logger.info("Total Records to be processes are " + str(len(sb.index)))
			self.write(self._errored,'errors')
		else:   
			return True    
	
	def create_new_products(self):
		attributes = modules.ProductAttributeValues(self.conf)
		self.attribute_values = attributes.get_attribute_values(None)
		self.create_products()
		self.write(self.sb,'new_products')

class PricelistXLS(XLS):

	def __init__(self, conf,saboo_path='Saboo_data.xlsx',
				 sheet='None'):
		if conf and conf['xls'] and conf['xls']['root'] and conf['Modules']['name']:
			self.conf = conf
			self.root = conf['xls']['root']
			if not self.root.endswith('/'):
				self.root = self.root+'/'
			self.path = self.root+conf['xls']['xl_file']
			self.modules = conf['Modules']['name'].split(',')
			self.sheet = conf['xls']['sheet_name']
		else:
			_logger.error("Invalid Configuration - Cannot execute")
			raise Exception("Cannot process excel file")
		if conf['xls'] and conf['xls']['mode'] == 'auto':
			self.xlsx = pd.ExcelFile(self.path or saboo_path)
			self.original = pd.read_excel(self.xlsx,sheet_name=None)
			self.sb = self.original
		else:
			_logger.info("-----XLS not loaded in init------")

	def prepare(self,sheet):
		try:
			model = sheet.iloc[:,1:]
			_logger.debug("component columms ------> %s",model.iloc[2,5:].values)
			pricelist_columns = [ " ".join(str(x).split()) for x in model.iloc[2,5:].values]
			model = model[4:]
			model = model.reset_index(drop=True)
			pricelist_columns = ['Model','Variant','Color-Variant','Variant-1','Ex S/R Price']+pricelist_columns
			model.columns = pricelist_columns
			_logger.debug(model[model['Model'].str.upper().str.contains('COLOUR')==True].index.values[0])
			self.color_row = model[model['Model'].str.upper().str.contains('COLOUR')==True]
			_logger.debug(self.color_row)
			model = model[:self.color_row.index.values[0]-1]
			model.drop(model[model.isna().all(axis=1)==True].index.values)
			model.iloc[:,:2] = model.iloc[:,:2].fillna(method='ffill').astype('str')
			if model['Color-Variant'].isna().all():
				model.loc[:,['Color-Variant']] = model.loc[:,['Color-Variant']].fillna('').astype('str')
			else:
				model.loc[:,['Color-Variant']] = model.loc[:,['Color-Variant']].fillna(method='ffill').astype('str')
			if model['Variant-1'].isna().all():
				model.loc[:,['Variant-1']] = model.loc[:,['Variant-1']].fillna('').astype('str')
			else:
				model.loc[:,['Variant-1']] = model.loc[:,['Variant-1']].fillna(method='ffill').astype('str')
			model.iloc[:,4:] = model.iloc[:,4:].fillna(0).astype('int')
			model.loc[:,'Variant-1'] = model.loc[:,'Variant-1'].fillna('').astype('str')
			model = model.drop_duplicates(['Model','Variant','Color-Variant','Variant-1'],keep='first').reset_index(drop=True)
			return model
		except Exception as ex:
			_logger.exception(ex)
			return pd.DataFrame()
	
	def getPricelistColumns(self,sheet):
		# remove the first unwanted column
		model = sheet.iloc[:,1:]
		return [ " ".join(x.split()) for x in model.iloc[2,5:].values]


	def _validate(self,sheet):
		header_row = sheet.iloc[1,:].fillna("").astype(str)
		header_row = [x.upper() for x in header_row.values]
		header_column = sheet[sheet.columns[1]].str.upper()
		if 'MODEL' in header_row and header_row[5] and header_row[5].strip().startswith('EX') and header_column.str.contains('COLOUR').any():
			return True
		else:
			_logger.error("Invalid Sheet %s",len(sheet.columns))
			return False
		return False

	def handle_request(self,file,file_name = 'h1',company_id = 1,job_id = '5db168295e1e9f00115cd74b'):
		print('handle_request----')
		self.xlsx = pd.ExcelFile(file)
		self.original = pd.read_excel(self.xlsx,sheet_name=None)
		self.sb = self.original
		return self.execute(file_name,company_id,job_id)
	
	def execute_sheet(self,sheet,pricelist_id):

		sheet_result = {'name':sheet,'status':'','values':''}
		try:
			_logger.info("Started Processing sheet  %s -----------",sheet)
			if self._validate(self.sb[sheet]):
				model = self.create_pricelist_items(self.sb[sheet],pricelist_id)
				if not model.empty:
					sheet_result['values'] = pricelist_items.create(model.to_dict(orient='records'),pricelist_id,self.getPricelistColumns(self.sb[sheet]),None)
					status = 'success'
				else:
					_logger.error("Could not Prepare sheet")
					sheet_result['status'] = 'incorrect sheet'
					sheet_result['values'] = 'Sheet has problems'
					status = 'error'
			else:
				_logger.error("Validation Failed !!!!!")
				sheet_result['status'] = 'validation failed'
				sheet_result['values'] ='Not a Valid Format'
				status = 'error'
		except Exception as ex:
			_logger.exception(ex)
			sheet_result['status'] = 'error'
			sheet_result['values'] = str(ex) 
			status = 'error'
		_logger.info("Finished Processing sheet  %s -----------",sheet)
		return sheet_result

	def execute_new(self,file_name = 'h1',company_id = 1,job_id = '5db168295e1e9f00115cd74b'):
		pricelist_items = modules.PricelistItem(self.conf)
		pricelist_id = self.create_price_list(file_name,company_id)
		_logger.info("the pricelist created is %s ",pricelist_id)
		result = []
		status = 'success'
		process_threads = []
		task = api.PriceListJobApi(self.conf)
		_logger.info("The pricelist file with sheets %s read and number of sheets is  %s ",self.sb.keys(), str(len(self.sb.keys())))
		for sheet in self.sb:
			process = Thread(target=self.execute_sheet, args=[sheet,pricelist_id])
			process.start()
			process_threads.append(process)
		for process in process_threads:
			sheet_result = process.join()
			result.append(sheet_result)    
		task.finishJob(job_id, status)

	def execute(self,file_name = 'h1',company_id = 1,job_id = '5db168295e1e9f00115cd74b'):
		pricelist_items = modules.PricelistItem(self.conf)
		pricelist_id = self.create_price_list(file_name,company_id)
		_logger.debug("the pricelist created is %s ",pricelist_id)
		result = []
		status = 'success'
		task = api.PriceListJobApi(self.conf)
		_logger.debug("The pricelist file with sheets %s read and number of sheets is  %s ",self.sb.keys(), str(len(self.sb.keys())))
		for sheet in self.sb:
			sheet_result = {'name':sheet,'status':'','values':''}
			try:
				_logger.info("Started Processing sheet  %s -----------",sheet)
				if self._validate(self.sb[sheet]):
					model = self.create_pricelist_items(self.sb[sheet],pricelist_id)
					if not model.empty:
						sheet_result['values'] = pricelist_items.create(model.to_dict(orient='records'),pricelist_id,self.getPricelistColumns(self.sb[sheet]),None)
						status = 'success'
					else:
						_logger.error("Could not Prepare sheet")
						sheet_result['status'] = 'incorrect sheet'
						sheet_result['values'] = 'Sheet has problems'
						status = 'error'
				else:
					_logger.error("Validation Failed !!!!!")
					sheet_result['status'] = 'validation failed'
					sheet_result['values'] ='Not a Valid Format'
					status = 'error'
			except Exception as ex:
				_logger.exception(ex)
				sheet_result['status'] = 'error'
				sheet_result['values'] = str(ex) 
				status = 'error'
			_logger.info("Finished Processing sheet  %s -----------",sheet)
			result.append(sheet_result)
		task.finishJob(job_id, status)    
		return result
		
		
	def getColors(self,sheet):
		colors = self.color_row.values[0][1]
		_logger.debug("The colors in get colors %s",colors)
		if colors:    
			col_array = colors.split(':')
			_logger.debug("The color array in get colors %s",col_array)
			if col_array and len(col_array) >2:
				#handle metallic and nonmetallic 
				mcolors = col_array[1].strip().split(',')
				if type(col_array[2].strip()) is str:
					nonm = [col_array[2].strip()]
				else:
					nonm = col_array[2].strip()
				return {'Metallic':mcolors[:len(mcolors)-1],'NonMetallic':nonm or False}
			if col_array and len(col_array) ==1:
				#handle colors for all variants
				_logger.debug("The dict in get colors %s",{'Colors':col_array[0].strip().split(',')})
				return {'Colors':col_array[0].strip().split(',')}

	def transform_variant_colors(self,model,colors):
		c_model = pd.DataFrame()
		for index in model.index.values:
			row = model.loc[index:index,:].copy()
			if  'Colors' in colors and not row['Color-Variant'].values[0]:
				for color in colors['Colors']:
					if color:
						row.loc[:,'Color'] = color.strip()
						c_model = c_model.append(row,ignore_index=True)
			else:
				if row['Color-Variant'].values[0] == 'M':
					for color in colors['Metallic']:
						if color:
							row.loc[:,'Color'] = color.strip()
							c_model = c_model.append(row,ignore_index=True)
				if row['Color-Variant'].values[0] == 'NM':
					for color in colors['NonMetallic']:
						if color:
							row.loc[:,'Color'] = color.strip()
							c_model = c_model.append(row,ignore_index=True)
		return c_model

	def create_price_list(self,file_name,company_id):
		pricelist = modules.Pricelist(self.conf)
		return pricelist.create(file_name,company_id,None)

	def update_product_id(self,prods,attribute_values):
		sb = self.sb
		attribute_columns = ['COLOR','VARIANT']
		product_product = modules.ProductProduct(self.conf)
		prods['Product ID'] = product_product.create(prods.to_dict(orient='records'),attribute_values,attribute_columns,None)
		_logger.debug(" %s ------------------------------------------",prods)
		return prods


	def create_pricelist_items(self,sheet,pricelist_id):
		model = self.prepare(sheet)
		if not model.empty:
			_logger.debug(model['Color-Variant'])
			colors = self.getColors(model)
			_logger.debug("The colors are %s",colors)
			if colors:
				model = self.transform_variant_colors(model,colors)
				model = self.update_products(model)
				return model
			else:
				_logger.error("Error while preparing sheet - No Colors could be extracted")
				return pd.DataFrame()    
		else:
			_logger.error("Error while preparing sheet")
			return pd.DataFrame()


	def update_products(self, model):
			_logger.debug(model)
			arr = {}
			colors = model['Color'].values
			variants = model['Variant'].values
			col_vars = model['Color-Variant'].values
			var1_vars = model['Variant-1'].values
			for index in range(len(variants)):
				if col_vars[index]:
					variants[index] = variants[index] + '('+col_vars[index]+')'
				if var1_vars[index]:
					variants[index] = variants[index] + '('+var1_vars[index]+')'
			_logger.debug(" the variants ---- %s",variants)
			arr['COLOR'] = colors
			arr['VARIANT'] = variants
			_logger.info("-----Starting Attribute Creation-------")
			attributes = modules.ProductAttributes(self.conf)
			attribute_values = attributes.create(arr,None)
			_logger.info("-----End of Attribute Creation------- %s",attribute_values)
			_logger.info("---Starting Template Creation-------")
			prod_templates = []
			lis = {}
			lis['name'] = model['Model'][0]
			lis['values'] = [('COLOR',colors),('VARIANT',variants)]
			prod_templates.append(lis)
			product = modules.ProductTemplate(self.conf)
			template_ids = product.create(prod_templates,attribute_values,None)
			_logger.info("-----End of Template Creation-------")
			prods = model[['Model', 'Color', 'Variant']].copy()
			prods.columns = ['NAME','COLOR','VARIANT']
			prods.loc[:,'product_tmpl_id'] = template_ids[0]

			# update whole table with product_product id
			_logger.info("---Starting product Creation-------")
			_logger.debug("Length %s %s %s %s",len(prods), len(model['Variant']),"--------------------",model['Model'])
			prods = self.update_product_id(prods,attribute_values)
			_logger.info("-----End of Product Creation-------")
			_logger.debug("Length------ %s %s",len(prods), len(model['Variant']))
			model.loc[:,'product_id'] = prods['Product ID']
			return model   

