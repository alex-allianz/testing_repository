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

from osv import osv,fields

from tools import amount_to_text_en

class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'
    
    _columns = {    
        'amount_in_word' : fields.char("Amount in word" , size=128, readonly=True, states={'draft':[('readonly',False)]}),
        'allow_check' : fields.boolean('Allow Check Writing'), # attrs does not support '.' format and fields.relates get the value when v save the record
        'chk_seq' : fields.char("Check Number" , size=64, readonly=True),
        'chk_status' : fields.boolean("Check Status" ),
    }
    
    
    def _get_journal(self, cr, uid, context=None):
        '''
        Function to initialise the variable journal_id
        '''
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
        if context.get('invoice_id', False):
            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            return journal_id and journal_id[0] or False
        
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')

        ttype = context.get('type', 'bank')

        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        if context.get('write_check',False) :           
            res = journal_pool.search(cr, uid, [('allow_check_writing', '=', True)], limit=1)
        else :
            res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        return res and res[0] or False
        
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """ Inherited - add amount_in_word in return value dictionary 
            cr: cursor
            uid: user id
            ids: ids of account voucher
            partner_id: partner's id
            journal_id: journal's id
            price: price
            currency_id: id of currency using
            date: date
            context: context
        """
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or price

            #TODO : generic amount_to_text is not ready yet, otherwise language and currency can be passed accordingly
    #            currency_format =  self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.name
    #            if currency_format=='us':
    #                amount_in_word = amount_to_words(amount)
    #            else: 
    #                amount_in_word = amount_to_text(amount)
    #            
    #            default['value'].update({'amount_in_word':amount_in_word})
            
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id).allow_check_writing
                default['value'].update({'allow_check':allow_check_writing})
        return default
    
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype,
                                date, context=None):
        if context is None:
            context = {}
        invoice_ref = False
        invoice_id = []
        invoice_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        res = super(account_voucher,self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price,
                                                                  currency_id, ttype, date, context=context)
        if res['value']:
            if context.get('type', False) and context['type'] == 'payment':
                new_line = []
                for dr_lines in res['value']['line_dr_ids']:
                    dr_line_move_line_id = dr_lines['move_line_id']
                    move_id = move_line_obj.browse(cr, uid, dr_line_move_line_id, context=context)
                    if move_id and move_id.move_id:
                        invoice_id = invoice_obj.search(cr, uid, [('move_id', '=', move_id.move_id.id)], context=context)
                    for invoice in invoice_obj.browse(cr, uid, invoice_id, context=context):
                        invoice_ref = invoice.reference
                    if invoice_ref:
                        dr_lines.update(name = invoice_ref)
                    new_line.append(dr_lines)
                res['value']['line_dr_ids'] = new_line
        return res
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date,
                        payment_rate_currency_id, company_id, context=None):
        res = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id,
                                                           currency_id, ttype, date, payment_rate_currency_id,
                                                           company_id, context=context)
        amount = res and res['value'] and res['value']['paid_amount_in_company_currency'] and \
                 res['value']['paid_amount_in_company_currency'] or 0.00
        if amount and company_id:
            amount_in_words = self.convert(cr, uid, ids, amount, company_id, context=context)
            res['value']['amount_in_word'] = amount_in_words
        return res
    
    def convert(self, cr, uid, ids, amount, company_id, context=None):
        company_obj = self.pool.get('res.company')
        amt_en = amount
        if company_id:
            company = company_obj.browse(cr, uid, company_id, context=context)
            currency = company.currency_id and company.currency_id or False
            if currency:
                if currency.name == 'USD':
                    currency_name = 'Dollars'
                else:
                    currency_name = currency.name
                amt_en = amount_to_text_en.amount_to_text(amount, 'en', currency_name)
                if amt_en.endswith('Cents'):
                    amt_en = amt_en.replace('Cents', currency.sub_currency and currency.sub_currency or 'Cents')
                else:
                    amt_en = amt_en.replace('Cent', currency.sub_currency and currency.sub_currency or 'Cent')
        return amt_en
    
    def print_check(self, cr, uid, ids, context=None):
        res = super(account_voucher, self).print_check(cr, uid, ids, context=context)
        if res.get('report_name', False):
            if res['report_name'] == 'account.print.check.top':
                res['report_name'] = 'account.print.check.top1'
            elif res['report_name'] == 'account.print.check.middle':
                res['report_name'] = 'account.print.check.middle1'
            elif res['report_name'] == 'account.print.check.bottom':
                res['report_name'] = 'account.print.check.bottom1'
        return res
    
account_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
