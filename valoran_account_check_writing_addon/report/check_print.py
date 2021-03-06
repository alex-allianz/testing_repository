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
from account_check_writing.report.check_print import report_print_check


class report_print_check_add(report_print_check):
    
    def __init__(self, cr, uid, name, context):
        super(report_print_check_add, self).__init__(cr, uid, name, context)
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
                if address.state_id.code:
                    if ret:
                        ret += ', '
                    ret += address.state_id.code
            if address.zip:
                if ret:
                    ret += ' '
                ret += address.zip
        return ret
#    
    def get_lines(self, voucher_lines):
        result = []
        self.number_lines = len(voucher_lines)
        for i in range(0, self.number_lines):
            if not voucher_lines[i].amount: continue
            if i < self.number_lines:
                invoice_obj = voucher_lines[i].move_line_id.invoice or False
                res = {
                       'invoice': invoice_obj and invoice_obj.reference or '',
                       'date_original' : invoice_obj and invoice_obj.date_invoice or False,
                       'date_due' : voucher_lines[i].date_due,
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
                       'invoice': False,
                       'date_original': False
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
                      'report.account.print.check.top1',
                      'account.voucher',
                      'addons/valoran_account_check_writing_addon/report/check_print_top.rml',
                      parser=report_print_check_add, header=False)

report_sxw.report_sxw(
                      'report.account.print.check.middle1',
                      'account.voucher',
                      'addons/account_check_writing/report/check_print_middle.rml',
                      parser=report_print_check_add, header=False
                      )

report_sxw.report_sxw(
                      'report.account.print.check.bottom1',
                      'account.voucher',
                      'addons/account_check_writing/report/check_print_bottom.rml',
                      parser=report_print_check_add, header=False
                      )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
