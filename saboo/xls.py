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

_logger = logging.getLogger(__name__)

class XLS(object):
    sb = None
    xlsx = None
    _product_columns = {'NAME':str}
    _attribute_columns = {'COLOR':str}
    _attribute_cols = ['COLOR']
    _customer_attribute_columns = ['CNAME','TEL']
    _customer_columns = {'CNAME':str,'TEL':str,'ADD1':str,'CITY':str,'PCODE':str,'EMAIL':str}
    _products = None
   # modules = {1:'attributes',2:'products',3:'purchase_orders',4:'customers',5:'sale_orders',6:'enquiries'}
    _valid = True
    _mode = 'manual'
    
    def __init__(self, conf,saboo_path='Saboo_data.xlsx',
                 sheet='Sale'):
        if conf and conf['xls'] and conf['Modules']['name']:
            self.conf = conf
            self.path = conf['xls']['xl_file']
            self.modules = conf['Modules']['name'].split(",")
        else:
            _logger.error("Invalid Configuration - Cannot execute")    
        self.xlsx = pd.ExcelFile(self.path or saboo_path)
        self.original = pd.read_excel(self.xlsx, 'Sale',converters = self.get_all_columns())
        self.sb = self.original
        self.vendor_master =  pd.read_excel(self.xlsx, 'vendor')
        self.prepare()
    
    def get_all_columns(self):
        # need to dynamically load all fields - to do - CHANGE this !!!!
        #print(dict(self._product_columns.items()+self._attribute_columns.items()))
        all_cols = {}
        all_cols.update(self._product_columns)
        all_cols.update(self._attribute_columns)
        all_cols.update(self._customer_columns)
        #all_cols = dict(self._product_columns.items()+self._attribute_columns.items()+self._customer_columns.items())
        return all_cols

    @property
    def customer_attribute_columns(self):
        return self._customer_attribute_columns
    

    @property
    def products(self):
        return self._products
    
    @property
    def attribute_cols(self):
        return self._attribute_cols

    @property
    def product_attribute_cols(self):
        copy = self._attribute_cols.copy()
        copy.insert(0,'NAME')
        return copy
    @property
    def product_attribute_cols_ext(self):
        copy = self.product_attribute_cols
        copy.insert(0,'External NAME')
        return copy
   
    def write(self,df,filename):
        if df is not None:
            df.to_csv(self._output_dir+filename+'.csv')
        else:
            _logger.debug("Nothing to write")

    def _validate(self):
        sb = self.sb
        self._errored = sb[sb['ORDERNO'].isna() | sb['NAME'].isna() | sb['CNAME'].isna() | sb['ORDERDATE'].isna()] 
        if(len(self._errored.index)>0):
            _logger.error("Sheet has " + str(len(self._errored.index))+" invalid records")
            self.sb = sb.drop(self._errored.index.values)
            # Cleaning up indexes
            self.sb.reset_index(drop=True)
            self.write(self._errored,'errors')
        else:   
            return True

    def prepare(self):
        conf = self.conf['xls']
        self._mode = self.conf['xls']['mode']
        output_dir = conf['output']
        op = os.path.join(output_dir,conf['version'])
        if op and not os.path.isdir(op):
            os.makedirs(op)
        _logger.debug("The outut directory is"+op) 
        self._output_dir = op+'/'
        if not self._check_order_nos:
            raise ValueError("Invalid Configuration")
        self._original = self.sb.copy()
        _logger.debug("ignore errors value"+conf['ignore_errors'])
        if self._validate() or conf['ignore_errors'] == '1':
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
        gp_prods = sb.groupby([sb[x].str.upper() for x in self.product_attribute_cols])
        prod_id = 0
        products = pd.DataFrame()
        for name,group in gp_prods:
            temp = pd.DataFrame()
            sb.loc[group.index.values,'External NAME'].apply(lambda row:str(prod_id))
            temp = sb.loc[group.index.values[:1]][self.product_attribute_cols_ext]
            products = pd.concat([products,temp])
            prod_id += 1
        self._products = products
        _logger.debug(self._products)

    
    def prepareCustomers(self):
        sb = self.sb
        sb['Customer/External ID'] = sb.index
        sb['Customer/External ID'] =sb['Customer/External ID'].apply(lambda index: "customer_template_"+str(index))
        sb.loc[:,'CDUP'] = sb.duplicated(self._customer_attribute_columns,False).values
        gp_cust = sb[sb['CDUP'] == True].groupby(self.customer_attribute_columns,sort=False)
        for name,group in gp_cust:
            group.loc[group.index.values[1:],'Customer/External ID'] = group.loc[group.index.values[:1],'Customer/External ID'].values[0]
    
    def deduplicate(self,sb,list_cols):
        dedup = pd.DataFrame()
        for col in list_cols:
            sb[col] = sb[col].str.upper()
        dedup = sb.drop_duplicates(list_cols,keep='first')
        return dedup
    
    def getColumnDict(self,list_cols):
        d = {list_cols[i]:[] for i in range(0,len(list_cols))}
        return d 

    def _check_order_nos(self):
        if not self.sb:
            return False
        else:
            return True
    def execute(self):
        if self._valid:
            _logger.info("Processing "+str(self.sb['ORDERNO'].count())+" Records")
            _logger.info("The modules to be executed are " + str(self.modules) + " in mode " + self._mode)
            for module in self.modules:
               # module = self.modules[key]
                method = 'create_'+module
                if self._mode is 'manual':
                    method  = method+'_manual'
                _logger.info("START CREATING ---> "+module.upper())
                start = datetime.now()    
                self.write(getattr(self,method)(),module)
                finish = datetime.now() - start
                finish_time = int(finish.total_seconds()/60)
                _logger.info("END CREATING ---> "+module.upper() + " - Finished in - "+str(finish_time if finish_time >0 else finish.total_seconds()))
        else:
            _logger.error("Cannot execute with invalid data")
    
    def create_attributes(self):
        attributes = modules.ProductAttributes(self.conf)
        prods = self._products
        self.attribute_values = attributes.create({attribute:prods.loc[prods.duplicated(attribute)<1,attribute].sort_values().values for attribute in self.attribute_cols},None)
        _logger.info("Number of attributes created --> "+str(len(self.attribute_values)))


    def create_attributes_manual(self):
        attribs = self._products
        final = pd.DataFrame()
        for col in self.attribute_cols:
            af = pd.DataFrame()
            af['value_ids/name'] = attribs.loc[attribs.duplicated(col)<1,col].values
            af.loc[0,'name'] = col
            af.loc[0,'Type'] = "Select"
            final = pd.concat([final,af])
        return final

    def _get_product_id(self,df):
        for column in self.attribute_cols:
            value_id = [x for x,y in self.attribute_values[column]['values'] if y == df[column]]
        print("done with "+df['NAME']+df['COLOR'])
        if len(value_id) > 1:
            raise Exception("Product not unique - ERROR")
        product = modules.ProductProduct(self.conf)
        value = product.find_product(df['NAME'],value_id,None)
        return value[0]

    def create_products(self):
        prod_templates = []
        gp_prods = self._products.groupby([self._products['NAME'].str.upper()])
        for name,group in gp_prods:
            template = {'name':name,'values':[(x,group[x].values) for x in self.attribute_cols]}
            prod_templates.append(template)
        product = modules.ProductTemplate(self.conf)
        template_ids = product.create(prod_templates,self.attribute_values,None)
        for index in range(len(template_ids)):
            prod_templates[index]['id'] = template_ids[index]
        self.product_templates = prod_templates
        # update whole table with product_product id
        self.update_product_id()
       
    
    def update_product_id(self):
        prods = self._products
        sb = self.sb
        product_product = modules.ProductProduct(self.conf)
        prods['Product ID'] = product_product.get_product_product_list(None)
        gp_prods = sb.groupby([sb[x].str.upper() for x in self.product_attribute_cols])
        prod_id = 0
        for name,group in gp_prods:
            _logger.debug(name)
            _logger.debug(group[self.product_attribute_cols])
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

    def getProductTemplateId(self,df):
        index = self._products.loc[self._products[self.product_attribute_cols].eq(df[self.product_attribute_cols]).all(axis='columns')>0,'index'].values
        if(pd.isna(df['ORDERNO'])):
            return
        if(len(index) != 1):
            raise Exception("Invalid Data - possible duplicate product Ids - length of index : " +str(index))
        else:
            return self._products.iloc[index[0]]['External NAME']

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
            return self.create_purchase_orders_manual()

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
