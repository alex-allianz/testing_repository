# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
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
from osv import osv, fields

class wizard_report(osv.osv_memory):
    _inherit = "wizard.report"
    _columns = {
        'show_earning': fields.boolean('Show Earnings Account'),
        'earning_account': fields.many2one('account.account', 'Earnings Account')
    }
    _defaults = {
        'show_earning': False
    }

    def print_report(self, cr, uid, ids, data, context=None):
        res = super(wizard_report, self).print_report(cr, uid, ids, data, context=context)
        if res['report_name'] == 'afr.1cols':
            res['report_name'] = 'afr.1cols.inherit'
        if res['report_name'] == 'afr.2cols':
            res['report_name'] = 'afr.2cols.inherit'
        if res['report_name'] == 'afr.analytic.ledger':
            res['report_name'] = 'afr.analytic.ledger.inherit'
        if res['report_name'] == 'afr.4cols':
            res['report_name'] = 'afr.4cols.inherit'
        if res['report_name'] == 'afr.5cols':
            res['report_name'] = 'afr.5cols.inherit'
        if res['report_name'] == 'afr.qtrcols':
            res['report_name'] = 'afr.qtrcols.inherit'
        if res['report_name'] == 'afr.13cols':
            res['report_name'] = 'afr.13cols.inherit'
        return res
wizard_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
