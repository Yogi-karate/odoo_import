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
import pandas as pd
import numpy as np

class XLS(object):
    sb = None
    xlsx = None
    _attribute_cols = ['SEATING','CAPACITY','FUEL','CYLINDER','UWEIGHT','TYPE','WBASE','COLOR']
    _customer_attribute_columns = ['CNAME','TEL']
    _products = None

    def __init__(self, saboo_path='/Users/tramm/saboo/analysis/Saboo_Suzuki_Data/Saboo_data.xlsx',
                 sheet='Sale'):
        self.xlsx = pd.ExcelFile(saboo_path)
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
        copy = self.product_attribute_cols.insert(0,'External NAME')
        return copy
    
    def prepare(self):
        if not self._check_order_nos:
            raise ValueError("Invalid Configuration")
        print("Setting Up Base Data from Xl File")    
        self._products = self.deduplicate(self.sb,self.product_attribute_cols)[self.product_attribute_cols].reset_index(drop=True).reset_index()
        #self._products['External ID'] = self._products['index'].apply(lambda index: "product_template_"+str(index))
        ##self._products['External NAME'] = self._products.apply(lambda df: df['NAME']+" (Prod : "+str(df['index'])+")",axis=1)
        ##self.sb['External NAME'] = self.sb.apply(self.getProductTemplateId,axis=1)

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
    def execute(self,path):
        if path:
            self.createAttributes().to_csv(path+'saboo_attributes.csv')
            print("Completed Attributes Import File")
            self.createProducts().to_csv(path+'saboo_products.csv')
            print("Completed Products Import File")
            self.createCustomers().to_csv(path+'saboo_customers.csv')
            print("Completed Customers Import File")
            self.createEnquiries().to_csv(path+'saboo_enquiries.csv')
            print("Completed Enquiries Import File")
            self.createPurchaseOrders().to_csv(path+'saboo_purchase.csv')
            print("Completed Customers Import File")
            self.createSaleOrders().to_csv(path+'saboo_sale_order.csv')
            print("Completed Sale Order Import File")
        else:
            raise Exception("Cannot execute without Location")

    def createAttributes(self):
        attribs = self._products
        final = pd.DataFrame()
        for col in self.attribute_cols:
            af = pd.DataFrame()
            af['value_ids/name'] = attribs.loc[attribs.duplicated(col)<1,col].values
            af.loc[0,'name'] = col
            af.loc[0,'Type'] = "Select"
            final = pd.concat([final,af])
        return final

    def createProducts(self):
        template_cols = ['External ID','Name','Product Attributes/ Attribute Values','Product Attributes/Attribute','Type','Tracking']
        prods = self._products
        tprod = prods.T.reset_index()
        final = pd.DataFrame()
        for col in range(prods['NAME'].count()):
            sample = pd.DataFrame()
            sample['Product Attributes/Attribute'] = tprod['index'][2:10].values
            sample['Product Attributes/ Attribute Values'] = tprod[col][2:10].values
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

    def createCustomers(self):
        cust = pd.DataFrame()
        cust_template = ['CUSTOMER NAME','Mobile','Phone','Email','Street','Street2','CITY','ZIP','T/R NO','Registration number','Name','Created On','ORDER NO']
        cust[['NAME','Mobile','Street','CITY','ZIP','Email']] = self.sb[['CNAME','TEL','ADD1','CITY','PCODE','EMAIL']]
        cust['Street2'] = self.sb.ADD1+" "+ self.sb.ADD2
        cust = self.deduplicate(cust,['NAME','Mobile'])
        cust['External ID'] = cust.reset_index()['index'].apply(lambda index: "customer_template_"+str(index))
        return cust

    def createPurchaseOrders(self):
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

    def createEnquiries(self):
        pipeline = pd.DataFrame()
        pipeline[['Name','Created on','Expected Revenue']] = self.sb[['NAME','ORDERDATE','EXSRPRICE']]
        pipeline['Notes'] = self.sb['ORDERNO'].apply(lambda ord: "Order Number : " + str(ord))
        pipeline['STAGE'] = "Won"
        pipeline['CUSTOMER/External ID'] = pipeline.reset_index()['index'].apply(lambda index: "customer_template_"+str(index))
        pipeline = self.deduplicate(pipeline,['Notes'])
        return pipeline

    def createSaleOrders(self):
        so = pd.DataFrame()
        so_template = ['Order Date','Order Lines/Scheduled Date','Vendor Reference','Order Lines/Description','Order Lines/Product Unit Of Measure/Database ID','Order Lines/Quantity','Order Lines/Unit Price','Order Lines/Taxes /Database ID','Vendor','Order Lines/Product','Status']
        #po[['Order Date','Order Lines/Scheduled Date','Order Lines/Description','Order Lines/Product','Order Lines/Unit Price']] = sb[['ORDERDATE','ORDERDATE','NAME','NAME','BASIC']]
        so[['Order Date','Order Lines/Product','Order Lines/Unit Price']] = self.sb[['ORDERDATE','External NAME','BASIC']]
        so[['ORDER REFERENCE','Order Lines/Description']] = self.sb[['ORDERNO','NAME']]
        so['Order Lines/Quantity'] = "1"
        so['CUSTOMER/External ID'] = so.reset_index()['index'].apply(lambda index: "customer_template_"+str(index))
        # Change to right tax value later -------
        so['Order Lines/Taxes/Database ID'] = "25"
        so['External ID'] = so.reset_index()['index'].apply(lambda index: "sale_order_template_"+str(index))
        so = self.deduplicate(so,['ORDER REFERENCE'])
        return so
