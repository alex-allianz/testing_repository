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
from osv import osv, fields
from tools.translate import _

class account_cashflow_report(osv.osv_memory):
    
    """
    This wizard will provide the account cash flow report by periods, between any two dates.
    """
    _name = 'account.cashflow.report'
    _inherit = "account.common.account.report"
    _description = 'Account Cash Flow Report'

    _columns = {
                }

    _defaults={
               'journal_ids': [],
               }

    def _print_report(self, cr, uid, ids, data, context=None):
        
        if context is None:
            context = {}
            
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.cashflow.r',
                'datas': data,
                }
        
account_cashflow_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
