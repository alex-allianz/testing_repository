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
import time
import datetime
from report import report_sxw
from tools import config
from tools.translate import _
from osv import osv
from operator import itemgetter
from account_financial_report.report.parser import account_balance

class account_balance_inherit(account_balance):
    def __init__(self, cr, uid, name, context):
        super(account_balance_inherit, self).__init__(cr, uid, name, context)
            
    def lines(self, form, level=0):
        """
        Returns all the data needed for the report lines
        (account info plus debit/credit/balance in the selected period
        and the full year)
        """
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        self.show_earnings = False
        if form['show_earning'] and isinstance(form['earning_account'], tuple):
            form['earning_account'] = form['earning_account'][0]
        def _get_children_and_consol(cr, uid, ids, level, context={},change_sign=False):
            aa_obj = self.pool.get('account.account')
            ids2=[]
            for aa_brw in aa_obj.browse(cr, uid, ids, context):
                if aa_brw.child_id and aa_brw.level < level and aa_brw.type !='consolidation':
                    if not change_sign:
                        ids2.append([aa_brw.id,True, False,aa_brw])
                    ids2 += _get_children_and_consol(cr, uid, [x.id for x in aa_brw.child_id], level, context,change_sign=change_sign)
                    if change_sign:
                        ids2.append(aa_brw.id) 
                    else:
                        ids2.append([aa_brw.id,False,True,aa_brw])
                else:
                    if change_sign:
                        ids2.append(aa_brw.id) 
                    else:
                        ids2.append([aa_brw.id,True,True,aa_brw])
            return ids2

        #############################################################################
        # CONTEXT FOR ENDIND BALANCE                                                #
        #############################################################################

        def _ctx_end(ctx):
            ctx_end = ctx
            ctx_end['filter'] = form.get('filter','all')
            ctx_end['fiscalyear'] = fiscalyear.id
            #~ ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',False)])
            
            if ctx_end['filter'] not in ['bydate','none']:
                special = self.special_period(form['periods'])
            else:
                special = False
            
            if form['filter'] in ['byperiod', 'all']:
                if special:
                    ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('id','in',form['periods'] or ctx_end.get('periods',False))])
                else:
                    ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('id','in',form['periods'] or ctx_end.get('periods',False)),('special','=',False)])
                    
            if form['filter'] in ['bydate','all','none']:
                ctx_end['date_from'] = form['date_from']
                ctx_end['date_to'] = form['date_to']
            
            return ctx_end.copy()
        
        def missing_period(ctx_init):
            
            ctx_init['fiscalyear'] = fiscalyear_obj.search(self.cr, self.uid, [('date_stop','<',fiscalyear.date_start)],order='date_stop') and \
                                fiscalyear_obj.search(self.cr, self.uid, [('date_stop','<',fiscalyear.date_start)],order='date_stop')[-1] or []
            ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',ctx_init['fiscalyear']),('date_stop','<',fiscalyear.date_start)])
            return ctx_init
        #############################################################################
        # CONTEXT FOR INITIAL BALANCE                                               #
        #############################################################################
        
        def _ctx_init(ctx):
            ctx_init = self.context.copy()
            ctx_init['filter'] = form.get('filter','all')
            ctx_init['fiscalyear'] = fiscalyear.id

            if form['filter'] in ['byperiod', 'all']:
                ctx_init['periods'] = form['periods']
                if not ctx_init['periods']:
                    ctx_init = missing_period(ctx_init.copy())
                date_start = min([period.date_start for period in period_obj.browse(self.cr, self.uid, ctx_init['periods'])])
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('date_stop','<=',date_start)])
            elif form['filter'] in ['bydate']:
                ctx_init['date_from'] = fiscalyear.date_start
                ctx_init['date_to'] = form['date_from']
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('date_stop','<=',ctx_init['date_to'])])
            elif form['filter'] == 'none':
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',True)])
                date_start = min([period.date_start for period in period_obj.browse(self.cr, self.uid, ctx_init['periods'])])
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('date_start','<=',date_start),('special','=',True)])
            
            return ctx_init.copy()

        def z(n):
            return abs(n) < 0.005 and 0.0 or n
                

        self.from_currency_id = self.get_company_currency(form['company_id'] and type(form['company_id']) in (list,tuple) and form['company_id'][0] or form['company_id'])
        if not form['currency_id']:
            self.to_currency_id = self.from_currency_id
        else:
            self.to_currency_id = form['currency_id'] and type(form['currency_id']) in (list, tuple) and form['currency_id'][0] or form['currency_id']
        selected_accounts = []
        if form.has_key('account_list') and form['account_list']:
            selected_accounts = form['account_list']
            account_ids = form['account_list']
            del form['account_list']
        
        credit_account_ids = self.get_company_accounts(form['company_id'] and type(form['company_id']) in (list,tuple) and form['company_id'][0] or form['company_id'],'credit')
        
        debit_account_ids = self.get_company_accounts(form['company_id'] and type(form['company_id']) in (list,tuple) and form['company_id'][0] or form['company_id'],'debit')

        if form.get('fiscalyear'):
            if type(form.get('fiscalyear')) in (list,tuple):
                fiscalyear = form['fiscalyear'] and form['fiscalyear'][0]
            elif type(form.get('fiscalyear')) in (int,):
                fiscalyear = form['fiscalyear']
        fiscalyear = fiscalyear_obj.browse(self.cr, self.uid, fiscalyear)

        ################################################################
        # Get the accounts                                             #
        ################################################################

        account_ids = _get_children_and_consol(self.cr, self.uid, account_ids, form['display_account_level'] and form['display_account_level'] or 100,self.context)
        
        credit_account_ids = _get_children_and_consol(self.cr, self.uid, credit_account_ids, 100,self.context,change_sign=True)
        
        debit_account_ids = _get_children_and_consol(self.cr, self.uid, debit_account_ids, 100,self.context,change_sign=True)
        
        credit_account_ids = list(set(credit_account_ids) - set(debit_account_ids))

        #
        # Generate the report lines (checking each account)
        #
        
        tot_check = False
        
        if not form['periods']:
            form['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',False)],order='date_start asc')
            if not form['periods']:
                raise osv.except_osv(_('UserError'),_('The Selected Fiscal Year Does not have Regular Periods'))

        if form['columns'] == 'qtr':
            period_ids = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',False)],order='date_start asc')
            a=0
            l=[]
            p=[]
            for x in period_ids:
                a+=1
                if a<3:
                        l.append(x)
                else:
                        l.append(x)
                        p.append(l)
                        l=[]
                        a=0
            
            #~ period_ids = p

        elif form['columns'] == 'thirteen':
            period_ids = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',False)],order='date_start asc')

        if form['columns'] == 'qtr':
            tot_bal1 = 0.0
            tot_bal2 = 0.0
            tot_bal3 = 0.0
            tot_bal4 = 0.0
            tot_bal5 = 0.0

        elif form['columns'] == 'thirteen':
            tot_bal1 = 0.0
            tot_bal2 = 0.0
            tot_bal3 = 0.0
            tot_bal4 = 0.0
            tot_bal5 = 0.0
            tot_bal6 = 0.0
            tot_bal7 = 0.0
            tot_bal8 = 0.0
            tot_bal9 = 0.0
            tot_bal10 = 0.0
            tot_bal11 = 0.0
            tot_bal12 = 0.0
            tot_bal13 = 0.0

        else:
            
            ctx_init = _ctx_init(self.context.copy())
            ctx_end = _ctx_end(self.context.copy())

            tot_bin = 0.0
            tot_deb = 0.0
            tot_crd = 0.0
            tot_ytd = 0.0
            tot_eje = 0.0
        
        res = {}
        result_acc = []
        tot = {}   
        ############################3
        net_balance = 0.0   
        temp_earning = {}  
        for par_id in selected_accounts:
            aa_brw_init = account_obj.browse(self.cr, self.uid, par_id, ctx_init)
            aa_brw_end  = account_obj.browse(self.cr, self.uid, par_id, ctx_end)

            i1,d1,c1 = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
            b1 = z(i1+d1-c1)
            net_balance += b1
        ################################
        for aa_id in account_ids:
            id = aa_id[0]

            #
            # Check if we need to include this level
            #
            if not form['display_account_level'] or aa_id[3].level <= form['display_account_level']:
                res = {
                'id'        : id,
                'type'      : aa_id[3].type,
                'code'      : aa_id[3].code,
                'name'      : (aa_id[2] and not aa_id[1]) and 'TOTAL %s'%(aa_id[3].name.upper()) or aa_id[3].name,
                'parent_id' : aa_id[3].parent_id and aa_id[3].parent_id.id,
                'level'     : aa_id[3].level,
                'label'     : aa_id[1],
                'total'     : aa_id[2],
                'change_sign' : credit_account_ids and (id  in credit_account_ids and -1 or 1) or 1
                }
                print res,'\n\n\n'
                
                if form['columns'] == 'qtr':
                    pn = 1
                    for p_id in p:
                        form['periods'] = p_id
                        
                        ctx_init = _ctx_init(self.context.copy())
                        aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                        
                        ctx_end = _ctx_end(self.context.copy())
                        aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                        
                        if form['inf_type'] == 'IS':
                            d,c,b = map(z,[aa_brw_end.debit,aa_brw_end.credit,aa_brw_end.balance])
                            res.update({
                                'dbr%s'%pn: self.exchange(d),
                                'cdr%s'%pn: self.exchange(c),
                                'bal%s'%pn: self.exchange(b),
                            })
                        else:
                            i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                            b = z(i+d-c)
                            res.update({
                                'dbr%s'%pn: self.exchange(d),
                                'cdr%s'%pn: self.exchange(c),
                                'bal%s'%pn: self.exchange(b),
                            })
                            
                        pn +=1
            
                    form['periods'] = period_ids
                    
                    ctx_init = _ctx_init(self.context.copy())
                    aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                    
                    ctx_end = _ctx_end(self.context.copy())
                    aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                    
                    if form['inf_type'] == 'IS':
                        d,c,b = map(z,[aa_brw_end.debit,aa_brw_end.credit,aa_brw_end.balance])
                        res.update({
                            'dbr5': self.exchange(d),
                            'cdr5': self.exchange(c),
                            'bal5': self.exchange(b),
                        })
                    else:
                        i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                        b = z(i+d-c)
                        res.update({
                            'dbr5': self.exchange(d),
                            'cdr5': self.exchange(c),
                            'bal5': self.exchange(b),
                        })
                
                elif form['columns'] == 'thirteen':
                    pn = 1
                    for p_id in period_ids:
                        form['periods'] = [p_id]
                        
                        ctx_init = _ctx_init(self.context.copy())
                        aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                        
                        ctx_end = _ctx_end(self.context.copy())
                        aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                        
                        if form['inf_type'] == 'IS':
                            d,c,b = map(z,[aa_brw_end.debit,aa_brw_end.credit,aa_brw_end.balance])
                            res.update({
                                'dbr%s'%pn: self.exchange(d),
                                'cdr%s'%pn: self.exchange(c),
                                'bal%s'%pn: self.exchange(b),
                            })
                        else:
                            i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                            b = z(i+d-c)
                            res.update({
                                'dbr%s'%pn: self.exchange(d),
                                'cdr%s'%pn: self.exchange(c),
                                'bal%s'%pn: self.exchange(b),
                            })
                            
                        pn +=1
            
                    form['periods'] = period_ids
                    
                    ctx_init = _ctx_init(self.context.copy())
                    aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                    
                    ctx_end = _ctx_end(self.context.copy())
                    aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                    
                    if form['inf_type'] == 'IS':
                        d,c,b = map(z,[aa_brw_end.debit,aa_brw_end.credit,aa_brw_end.balance])
                        res.update({
                            'dbr13': self.exchange(d),
                            'cdr13': self.exchange(c),
                            'bal13': self.exchange(b),
                        })
                    else:
                        i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                        b = z(i+d-c)
                        res.update({
                            'dbr13': self.exchange(d),
                            'cdr13': self.exchange(c),
                            'bal13': self.exchange(b),
                        })
                
                else:

                    aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                    aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)

                    i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                    b = z(i+d-c)
                    res.update({
                        'balanceinit': self.exchange(i),
                        'debit': self.exchange(d),
                        'credit': self.exchange(c),
                        'ytd': self.exchange(d-c),
                    })
                
                    if form['inf_type'] == 'IS' and form['columns'] == 'one':
                        res.update({
                            'balance': self.exchange(d-c),
                        })
                    elif form['inf_type'] == 'BS' and form['columns'] == 'one' and form['show_earning']:
                        if form['earning_account'] == id:
                            self.show_earnings = True
                            parent_account = account_obj.browse(self.cr, self.uid, id)
                            
                            net_earning_balance = self.exchange(net_balance) + \
                                 2*self.exchange((aa_brw_end.debit - aa_brw_end.credit)) + self.exchange(b)
                            res.update({
                                'balance': net_earning_balance,
                            })
                            temp_earning.update({(form['inf_type'],form['columns']): {
                                'earning': self.exchange(b),
                                'net': net_earning_balance,
                                'diff': net_earning_balance - self.exchange(b),
                                'parent_id': parent_account.parent_id and parent_account.parent_id.id or False,
                                }
                            })
                        else:
                            
#                            earning_res = {
#                                'id'        : id,
#                                'type'      : aa_id[3].type,
#                                'code'      : aa_id[3].code,
#                                'name'      : (aa_id[2] and not aa_id[1]) and 'TOTAL %s'%(aa_id[3].name.upper()) or aa_id[3].name,
#                                'parent_id' : aa_id[3].parent_id and aa_id[3].parent_id.id,
#                                'level'     : aa_id[3].level,
#                                'label'     : aa_id[1],
#                                'total'     : aa_id[2],
#                                'change_sign' : credit_account_ids and (id  in credit_account_ids and -1 or 1) or 1
#                                }
                        
                            res.update({
                                'balance': self.exchange(b),
                            })
                    else:
                        res.update({
                            'balance': self.exchange(b),
                        })

                #
                # Check whether we must include this line in the report or not
                #
                to_include = False
                
                if form['columns'] in ('thirteen', 'qtr'):
                    to_test = [False]
                    if form['display_account'] == 'mov' and aa_id[3].parent_id:
                        # Include accounts with movements
                        for x in range(pn-1):
                            to_test.append(res.get('dbr%s'%x,0.0) >= 0.005 and True or False)
                            to_test.append(res.get('cdr%s'%x,0.0) >= 0.005 and True or False)
                        if any(to_test):
                            to_include = True
                        
                    elif form['display_account'] == 'bal' and aa_id[3].parent_id:
                        # Include accounts with balance
                        for x in range(pn-1):
                            to_test.append(res.get('bal%s'%x,0.0) >= 0.005 and True or False)
                        if any(to_test):
                            to_include = True
                            
                    elif form['display_account'] == 'bal_mov' and aa_id[3].parent_id:
                        # Include accounts with balance or movements
                        for x in range(pn-1):
                            to_test.append(res.get('bal%s'%x,0.0) >= 0.005 and True or False)
                            to_test.append(res.get('dbr%s'%x,0.0) >= 0.005 and True or False)
                            to_test.append(res.get('cdr%s'%x,0.0) >= 0.005 and True or False)
                        if any(to_test):
                            to_include = True
                    else:
                        # Include all accounts
                        to_include = True
                
                else:

                    if form['display_account'] == 'mov' and aa_id[3].parent_id:
                        # Include accounts with movements
                        if abs(d) >= 0.005 or abs(c) >= 0.005:
                            to_include = True
                    elif form['display_account'] == 'bal' and aa_id[3].parent_id:
                        # Include accounts with balance
                        if abs(b) >= 0.005:
                            to_include = True
                    elif form['display_account'] == 'bal_mov' and aa_id[3].parent_id:
                        # Include accounts with balance or movements
                        if abs(b) >= 0.005 or abs(d) >= 0.005 or abs(c) >= 0.005:
                            to_include = True
                    else:
                        # Include all accounts
                        to_include = True
                
                #~ ANALYTIC LEDGER
                if to_include and form['analytic_ledger'] and form['columns']=='four' and form['inf_type'] == 'BS' and res['type'] in ('other','liquidity','receivable','payable'):
                    res['mayor'] = self._get_analytic_ledger(res,ctx=ctx_end)
                else:
                    res['mayor'] = []
                
                
                if to_include:
                    result_acc.append(res)
                    #
                    # Check whether we must sumarize this line in the report or not
                    #
                    if form['tot_check'] and res['type'] == 'view' and res['level'] == 1 and (res['id'] not in tot):

                        if form['columns'] == 'qtr':
                            tot_check = True
                            #~ tot[res['id']] = True
                            tot_bal1 += res.get('bal1',0.0)
                            tot_bal2 += res.get('bal2',0.0)
                            tot_bal3 += res.get('bal3',0.0)
                            tot_bal4 += res.get('bal4',0.0)
                            tot_bal5 += res.get('bal5',0.0)

                        elif form['columns'] == 'thirteen':
                            tot_check = True
                            #~ tot[res['id']] = True
                            tot_bal1 += res.get('bal1',0.0)
                            tot_bal2 += res.get('bal2',0.0)
                            tot_bal3 += res.get('bal3',0.0)
                            tot_bal4 += res.get('bal4',0.0)
                            tot_bal5 += res.get('bal5',0.0)
                            tot_bal6 += res.get('bal6',0.0)
                            tot_bal7 += res.get('bal7',0.0)
                            tot_bal8 += res.get('bal8',0.0)
                            tot_bal9 += res.get('bal9',0.0)
                            tot_bal10 += res.get('bal10',0.0)
                            tot_bal11 += res.get('bal11',0.0)
                            tot_bal12 += res.get('bal12',0.0)
                            tot_bal13 += res.get('bal13',0.0)

                        else:
                            tot_check = True
                            #~ tot[res['id']] = True
                            tot_bin += res['balanceinit']
                            tot_deb += res['debit']
                            tot_crd += res['credit']
                            tot_ytd += res['ytd']
                            tot_eje += res['balance']

        if tot_check:
            str_label = form['lab_str']
            res2 = {
                    'type' : 'view',
                    'name': 'TOTAL %s'%(str_label),
                    'label': False,
                    'total': True,
            }
            if form['columns'] == 'qtr':
                res2.update(dict(
                            bal1 = tot_bal1,
                            bal2 = tot_bal2,
                            bal3 = tot_bal3,
                            bal4 = tot_bal4,
                            bal5 = tot_bal5,))
            elif form['columns'] == 'thirteen':
                res2.update(dict(
                            bal1 = tot_bal1,
                            bal2 = tot_bal2,
                            bal3 = tot_bal3,
                            bal4 = tot_bal4,
                            bal5 = tot_bal5,
                            bal6 = tot_bal6,
                            bal7 = tot_bal7,
                            bal8 = tot_bal8,
                            bal9 = tot_bal9,
                            bal10 = tot_bal10,
                            bal11 = tot_bal11,
                            bal12 = tot_bal12,
                            bal13 = tot_bal13,))

            else:
                aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)

                i,d,c = map(z,[aa_brw_init.balance,aa_brw_end.debit,aa_brw_end.credit])
                b = z(i+d-c)
                res2.update({
                        
                        'balance': net_balance,
                })
                
            result_acc.append(res2)
            
        if form['show_earning']:
            if form['inf_type'] == 'BS' and form['columns'] == 'one':
                if not self.show_earnings:
                    earning_obj = account_obj.browse(self.cr, self.uid,form['earning_account'] )
                    res = {
                        'id'        : id,
                        'type'      : 'view',
                        'code'      : earning_obj.code,
                        'name'      : earning_obj.name,
                        'parent_id' : earning_obj.parent_id and earning_obj.parent_id.id,
                        'level'     : earning_obj.level,
                        'label'     : False,
                        'total'     : True,
                        'change_sign' : 1}
                    if form['columns'] not in ('qtr','thirteen'):
                        res.update({
                        
                        'balance':self.exchange(net_balance),
                        })
                    result_acc.append(res)
                    return result_acc
                has_parent =  temp_earning[(form['inf_type'],form['columns'])]['parent_id'] or False
                while has_parent:
                    res_index_list = [(i,d) for i,d in enumerate(result_acc) if d['id'] == has_parent]
                    parent = False
                    for index in res_index_list:
                        result_acc[index[0]]['balance']=result_acc[index[0]]['balance'] + temp_earning[(form['inf_type'],form['columns'])]['diff']
                        parent = result_acc[index[0]]['parent_id']
                    has_parent = parent or False
        
        return result_acc
    
report_sxw.report_sxw('report.afr.1cols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full.rml',
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.2cols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_2_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.4cols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_4_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.analytic.ledger.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_4_cols_analytic_ledger.rml',
                       parser=account_balance_inherit, 
                       header=False)
                       
report_sxw.report_sxw('report.afr.5cols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_5_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)
                       
report_sxw.report_sxw('report.afr.qtrcols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_qtr_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.13cols.inherit', 
                      'wizard.report', 
                      'account_financial_report/report/balance_full_13_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: