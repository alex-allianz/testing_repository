# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-TODAY VNC (<http://www.vnc.biz>).
#   
#    Authors : VNC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#   
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
import pooler
from report import report_sxw
from account.report.account_financial_report import report_account_common
from account.report.common_report_header import common_report_header
from tools.translate import _

class report_account_cashflow_1(report_sxw.rml_parse, common_report_header):
    def __init__(self, cr, uid, name, context=None):
        
        super(report_account_cashflow_1, self).__init__(cr, uid, name, context=context)
        self.obj_pl = report_account_common(cr, uid, name, context=context)
        
        self.result_sum = {
                           'operating' : 0.0,
                           'investing' : 0.0,
                           'financial' : 0.0, 
                          }
        self.result = {}
        self.res_bl = {}
        self.result_temp = []
        
        self.localcontext.update({
                                    'time': time,
                                    'get_lines': self.get_lines,
                                    'get_lines_another': self.get_lines_another,
                                    'get_company': self._get_company,
                                    'get_currency': self._get_currency,
                                    'get_data':self.get_data,
                                    'get_pl_balance':self.get_pl_balance,
                                    'get_fiscalyear': self._get_fiscalyear,
                                    'get_account': self._get_account,
                                    'get_start_period': self.get_start_period,
                                    'get_end_period': self.get_end_period,
                                    'get_sortby': self._get_sortby,
                                    'get_filter': self._get_filter,
                                    'get_start_date':self._get_start_date,
                                    'get_end_date':self._get_end_date,
                                    'get_company':self._get_company,
                                    'get_current_cash': self.get_current_cash,
                                    'get_financing_balance': self._get_financing_balance,
                                    'get_operating_balance': self._get_operating_balance,
                                    'get_investing_balance': self._get_investing_balance,            
                                    'get_adjusted_operating_balance': self._get_adjusted_operating_balance,
                                    
                                })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
       
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
       
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
       
        return super(report_account_cashflow_1, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_financing_balance(self):
        return self.result_sum['financial']

    def _get_adjusted_operating_balance(self):
        return self.result_sum['operating']

    def _get_investing_balance(self):
        return self.result_sum['investing']

    def _get_operating_balance(self):
        
        operating_balance = self.result_sum['operating']
        
        return operating_balance 

    def get_current_cash(self):
        return self._get_operating_balance() + self.result_sum['financial'] + self.result_sum['investing'] + self.res_bl['balance']

    def get_pl_balance(self):
        return self.res_bl['balance']
        
    def get_data(self,data):
        
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        
        """ 
            Getting Profit or Loss Balance from profit and Loss report 
        
        """
        
        sr_ids = self.pool.get('account.financial.report').search(cr, uid, [('name', '=', 'Balance Sheet')])
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, sr_ids, context=data['form']['used_context'])
        
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):

            if report.name == 'Profit (Loss) to report':
                self.res_bl = {
                                'balance': report.balance *-1,
                              }

            
        account_pool = db_pool.get('account.account')
        currency_pool = db_pool.get('res.currency')

        types = [
                    'operating',
                    'investing',
                    'financial'
                ]
        
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)
        if data['form']['filter'] == 'filter_period':
            ctx['period_from'] = data['form'].get('period_from', False)
            ctx['period_to'] =  data['form'].get('period_to', False)
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form'].get('date_from', False)
            ctx['date_to'] =  data['form'].get('date_to', False)
        ctx['state'] = data['form'].get('target_move', 'all')
        
        account_dict = {}
        account_id = data['form'].get('chart_account_id', False)
        
        account_ids = account_pool._get_children_and_consol(cr, uid, account_id, context=ctx)
        
        for typ in types:
            
            accounts_temp = []
            account_type = []
            
            if typ == 'operating':
                account_type = ['Intangible Assets', 'Current Assets', 'Loan and Advances', 'Misc. Expenditure', 'Reserve_Surplus', 'Current Liabilities', 'Provisions']
            elif typ == 'investing':
                account_type = ['Fixed Assets', 'Investment']
            elif typ == 'financial':
                account_type = ['Share Capital', 'Long Term Liabilities']
                
            accounts = account_pool.search(cr, uid, [('id','in',account_ids),('user_type.code1','in',account_type)], context=ctx)
            for account in account_pool.browse(cr, uid, accounts, context=ctx):
                    if account.type == 'view':
                        continue
                    difference = 0.0
                    account_dict = {
                                    'id': account.id,
                                    'code': account.code,
                                    'name': account.name,
                                    'level': account.level,
                                    'balance' : account.balance != 0.00 and account.balance * -1 or account.balance
                                    }
                    
                    self.result_sum[typ] += account_dict['balance']
                    accounts_temp.append(account_dict)
                
            self.result[typ] = accounts_temp
        return None

    def get_lines(self):
        
        return self.result_temp

    def get_lines_another(self, group):
        
        return self.result.get(group, [])

report_sxw.report_sxw('report.account.cashflow.r', 'account.account',
                      'addons/account_cashflow/report/account_cashflow.rml',
                       parser=report_account_cashflow_1,header='internal')
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
