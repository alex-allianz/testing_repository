# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) Allianz Technology
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

from osv import osv

from tools.safe_eval import safe_eval as eval

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)
        for purchase_obj in self.browse(cr, uid, ids, context=context):
            if res:
                invoice_obj.write(cr, uid, res, {'reference': purchase_obj.origin}, context=context)
        return res
    
purchase_order()

class purchase_line_invoice(osv.osv_memory):
    _inherit = 'purchase.order.line_invoice'
    
    def makeInvoices(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        order_line_obj = self.pool.get('purchase.order.line')
        invoice_obj = self.pool.get('account.invoice')
        res = super(purchase_line_invoice, self).makeInvoices(cr, uid, ids, context=context)
        domain = eval(res['domain'])
        invoice_ids = domain[0][2]
        if context.get('active_id', False):
            order = order_line_obj.browse(cr, uid, context['active_id'], context=context).order_id
            source_purchase = order and order.origin or False
        for invoice_id in invoice_ids:
            if source_purchase:
                invoice_obj.write(cr, uid, invoice_id, {'reference': source_purchase}, context=context)
        return res
    
purchase_line_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
