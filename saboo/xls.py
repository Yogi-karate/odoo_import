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

_logger = logging.getLogger(__name__)

class XLS(object):
    sb = None
    xlsx = None
    _attribute_cols = ['COLOR']
    _customer_attribute_columns = ['CNAME','TEL']
    _products = None
    modules = {1:'attributes',2:'products',3:'customers',4:'purchase_orders',5:'sale_orders',6:'enquiries'}
    _valid = True

    def __init__(self, conf,saboo_path='Saboo_data.xlsx',
                 sheet='Sale'):
        if conf:
            self.conf = conf
            self.path = conf['xl_file']
        self.xlsx = pd.ExcelFile(self.path or saboo_path)
        self.sb = pd.read_excel(self.xlsx, 'Sale')
        self.prepare()
    
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
        df.to_csv(self._output_dir+filename+'.csv')

    def _validate(self):
        sb = self.sb
        self._errored = sb[sb['ORDERNO'].isna() | sb['NAME'].isna() | sb['CNAME'].isna()]
        if(len(self._errored.index)>0):
            _logger.error("Sheet has " + str(len(self._errored.index))+" invalid records")
            self.sb = sb.drop(self._errored.index.values)
            self.write(self._errored,'errors')
        else:   
            return True

    def prepare(self):
        output_dir = self.conf['output']
        op = os.path.join(output_dir,self.conf['version'])
        if op and not os.path.isdir(op):
            os.makedirs(op)
        _logger.debug("The outut directory is"+op) 
        self._output_dir = op+'/'
        if not self._check_order_nos:
            raise ValueError("Invalid Configuration")
        self._original = self.sb.copy()
        _logger.debug("ignore errors value"+self.conf['ignore_errors'])
        if self._validate() or self.conf['ignore_errors'] == '1':
            _logger.debug("Setting Up Product Data from Xl File")    
            self.prepareProducts()
            _logger.debug("Setting Up Customer Data from Xl File")    
            self.prepareCustomers()
        else:
            _logger.error("Error in processing the xl file. Please fix and retry")
            self._valid = False


    def prepareProducts(self):
        gp_prods = self.sb.groupby([self.sb[x].str.upper() for x in self.product_attribute_cols],sort=False)
        prod_id = 0
        for name,group in gp_prods:
            self.sb.loc[group.index.values,'External NAME'] = group[:1]['NAME'].values[0]+" (Prod : "+str(prod_id)+")"
            prod_id += 1
        self._products = self.deduplicate(self.sb,self.product_attribute_cols)[self.product_attribute_cols_ext].reset_index(drop=True)
    
    def prepareCustomers(self):
        sb = self.sb
        sb['Customer/External ID'] = sb.reset_index()['index'].apply(lambda index: "customer_template_"+str(index))
        sb['TEL'] = sb['TEL'].fillna("").astype('str')
        gp_cust = sb.groupby([sb[x].str.upper() for x in self.customer_attribute_columns],sort=False)
        for name,group in gp_cust:
            if(group.index.size>1):
                sb.loc[group.index.values[1:],'Customer/External ID']= sb.loc[group.index.values[:1],'Customer/External ID'].values[0]    
    
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
            for key in self.modules.keys():
                module = self.modules[key]
                self.write(getattr(self,'create_'+module)(),module)
        else:
            _logger.error("Cannot execute with invalid data")

    def create_attributes(self):
        attribs = self._products
        final = pd.DataFrame()
        for col in self.attribute_cols:
            af = pd.DataFrame()
            af['value_ids/name'] = attribs.loc[attribs.duplicated(col)<1,col].values
            af.loc[0,'name'] = col
            af.loc[0,'Type'] = "Select"
            final = pd.concat([final,af])
        return final

    def create_products(self):
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
        cust_template = ['CUSTOMER NAME','Mobile','Phone','Email','Street','Street2','CITY','ZIP','T/R NO','Registration number','Name','Created On','ORDER NO']
        cust[['NAME','Mobile','Street','CITY','ZIP','Email','External ID']] = self.sb[['CNAME','TEL','ADD1','CITY','PCODE','EMAIL','Customer/External ID']]
        cust['Street2'] = self.sb.ADD1+" "+ self.sb.ADD2
        cust = self.deduplicate(cust,['NAME','Mobile'])
        return cust

    def create_purchase_orders(self):
        po = pd.DataFrame()
        po_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference','Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID','Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID','Vendor','Order Lines/Product','Status']
        #po[['Order Date','Order Lines/Scheduled Date','Order Lines/Description','Order Lines/Product','Order Lines/Unit Price']] = sb[['ORDERDATE','ORDERDATE','NAME','NAME','BASIC']]
        po[['Order Date','Order Lines/Product','Order Lines/Unit Price']] = self.sb[['ORDERDATE','External NAME','BASIC']]
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
        pipeline = pd.DataFrame()
        pipeline[['Name','Created on','Expected Revenue','CUSTOMER/External ID']] = self.sb[['NAME','ORDERDATE','EXSRPRICE','Customer/External ID']]
        pipeline['Notes'] = self.sb['ORDERNO'].apply(lambda ord: "Order Number : " + str(ord))
        pipeline['STAGE'] = "Won"
        pipeline = self.deduplicate(pipeline,['Notes'])
        return pipeline

    def create_sale_orders(self):
        so = pd.DataFrame()
        so_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference','Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID','Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID','Vendor','Order Lines/Product','Status']
        #po[['Order Date','Order Lines/Scheduled Date','Order Lines/Description','Order Lines/Product','Order Lines/Unit Price']] = sb[['ORDERDATE','ORDERDATE','NAME','NAME','BASIC']]
        so[['Order Date','Order Lines/Product','Order Lines/Unit Price','CUSTOMER/External ID']] = self.sb[['ORDERDATE','External NAME','BASIC','Customer/External ID']]
        so[['ORDER REFERENCE','Order Lines/Description']] = self.sb[['ORDERNO','NAME']]
        so['Order Lines/Quantity'] = "1"
        # Change to right tax value later -------
        so['Order Lines/Taxes/Database ID'] = "25"
        so['External ID'] = so.reset_index()['index'].apply(lambda index: "sale_order_template_"+str(index))
        so = self.deduplicate(so,['ORDER REFERENCE'])
        return so
