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

from osv import osv

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        purchase_obj = self.pool.get('purchase.order')
        invoice_obj = self.pool.get('account.invoice')
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type,
                                                               context=context)
        if context.get('inv_type', False) and context['inv_type'] == 'in_invoice':
            for picking_id in res:
                picking_obj = self.browse(cr, uid, picking_id, context=context)
                reference_pur = picking_obj.purchase_id and picking_obj.purchase_id.origin or False
                if reference_pur:
                    invoice_obj.write(cr, uid, res[picking_id], {'reference': reference_pur}, context=context)
        return res
stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
