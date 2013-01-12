# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 Allianz Technology
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
from report import report_sxw


class report_print_check_inherit(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(report_print_check_inherit, self).__init__(cr, uid, name, context=None)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
                                  'time': time,
                                  'get_lines': self.get_lines,
                                  'fill_stars': self.fill_stars,
                                  'get_zip_line': self.get_zip_line,
                                 })
        
    def get_zip_line(self, address):
        '''
        Get the address line
        '''
        ret = ''
        if address:
            if address.city:
                ret += address.city
            if address.state_id:
                if address.state_id.name:
                    if ret:
                        ret += ', '
                    ret += address.state_id.name
            if address.zip:
                if ret:
                    ret += ' '
                ret += address.zip
        return ret
#    
    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, min(10, self.number_lines)):
            if i < self.number_lines:
                res = {
                       'date_due': voucher_lines[i].date_due,
                       'name': voucher_lines[i].name,
                       'amount_original': voucher_lines[i].amount_original and voucher_lines[i].amount_original or False,
                       'amount_unreconciled': voucher_lines[i].amount_unreconciled and voucher_lines[i].amount_unreconciled or False,
                       'amount': voucher_lines[i].amount and voucher_lines[i].amount or False,
                      }
            else :
                res = {
                       'date_due': False,
                       'name': False,
                       'amount_original': False,
                       'amount_due': False,
                       'amount': False,
                      }
            result.append(res)
        return result
    
    def fill_stars(self, amount):
        if len(amount) < 100:
            stars = 100 - len(amount)
            return ' '.join([amount, '*' * stars])
        else:
            return amount
        
report_sxw.report_sxw(
                      'report.account.print.check.top.inherit',
                      'account.voucher',
                      'addons/account_check_writing/report/check_print_top.rml',
                      parser=report_print_check_inherit, header=False)

report_sxw.report_sxw(
                      'report.account.print.check.middle.inherit',
                      'account.voucher',
                      'addons/account_check_writing/report/check_print_middle.rml',
                      parser=report_print_check_inherit, header=False
                      )

report_sxw.report_sxw(
                      'report.account.print.check.bottom.inherit',
                      'account.voucher',
                      'addons/account_check_writing/report/check_print_bottom.rml',
                      parser=report_print_check_inherit, header=False
                      )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
