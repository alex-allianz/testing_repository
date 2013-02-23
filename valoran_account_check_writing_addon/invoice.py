# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class invoice(osv.osv):
    _inherit = 'account.invoice'

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        res = super(invoice, self).invoice_pay_customer(cr, uid, ids, context=context)
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        if res:
            res['context'].update({'default_inv_reference': inv.reference})
        return res
    
    def _get_reference_type_inherit(self, cr, uid, context=None):
        return [('none', ("Supplier's Invoice #:"))]
    
    _columns = {
    'reference': fields.char('Invoice Reference', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="The partner reference of this invoice."),
    'reference_type': fields.selection(_get_reference_type_inherit, 'Reference Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
    }

invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
