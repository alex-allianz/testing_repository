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
from osv import osv,fields
from tools import config
from tools.translate import _

class account_account_type(osv.osv):
    
    _inherit = "account.account.type"    
    
    _columns = {
    
                'code': fields.char('Code', size=32, required=False),
                'code1': fields.selection([('Fixed Assets','Fixed Assets'),
                                           ('Intangible Assets','Intangible Assets'),
                                           ('Investment','Investment'),
                                           ('Current Assets','Current Assets'),
                                           ('Cash & Bank','Cash & Bank'),
                                           ('Loan and Advances','Loan and Advances'),
                                           ('Misc. Expenditure','Misc. Expenditure'),
                                           ('Share Capital','Share Capital'),
                                           ('Reserve_Surplus','Reserve & Surplus'),
                                           ('Long Term Liabilities','Long Term Liabilities'),
                                           ('Current Liabilities','Current Liabilities'),
                                           ('Provisions','Provisions'),
                                           ('Direct Expenses','Direct Expenses'),
                                           ('Indirect Expenses','Indirect Expenses'),
                                           ('Direct Income','Direct Income'),
                                           ('Indirect Income','Indirect Income'),
                                           ('view','View')
                                          ], 'Code'),
                }

account_account_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: