# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Allianz Technology, A subsidiary of SAT Group, Inc
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

class check_report(osv.osv_memory):
    _name = "check.report"
    _description = "Check Report Generator"
    _columns = {
        'filter': fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')],'Filter By',help="If you will select the 'By Date and Period' filter, first it will give preference to periods and then to date range.", required=True),
        'fiscalyear': fields.many2one('account.fiscalyear','Fiscal Year' ,required=True),
        'periods': fields.many2many('account.period','rel_wizard_period','wizard_id','period_id','Periods'), 
        'start_period': fields.many2one('account.period', 'Start Period'),
        'end_period': fields.many2one('account.period', 'End Period'),
        'date_to': fields.date('End Date'),
        'date_from': fields.date('Start Date'),
        'partner_ids': fields.many2many('res.partner', string='Filter on partner',
                                         help="Only selected partners will be printed. Leave empty to print all partners.")
    }
            
    _defaults = {
        'filter': lambda *a:'byperiod',
        'fiscalyear': lambda self, cr, uid, c: self.pool.get('account.fiscalyear').find(cr, uid),
             
    }
    
    def onchange_start_period(self, cr, uid, ids, filter, period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_start
            res['value'].update({'date_from':periods})
            return res
   
    def onchange_end_period(self, cr, uid, ids, filter, period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_stop
            res['value'].update({'date_to':periods})
            return res
    
    def onchange_date_from(self, cr, uid, ids, date_from, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_from:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_from ), ('date_stop','>=', date_from),('special','=',False)], context=context)
            if periods:
                periods_from = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'org_periods_from':periods_from.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')
    
    def onchange_date_to(self, cr, uid, ids, date_to, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_to:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_to ), ('date_stop','>=', date_to),('special','=',False)], context=context)
            if periods:
                periods_to = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'org_periods_to':periods_to.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ') 
    
    def period_span(self, cr, uid, ids, fy_id, context=None):
        if context is None:
            context = {}
        
        ap_obj = self.pool.get('account.period')
        fy_id = fy_id and type(fy_id) in (list,tuple) and fy_id[0] or fy_id
        if not ids:
            #~ There is no periods
            return ap_obj.search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)],order='date_start asc')
        
        ap_brws = ap_obj.browse(cr, uid, ids, context=context)
        date_start = min([period.date_start for period in ap_brws])
        date_stop = max([period.date_stop for period in ap_brws])
        
        return ap_obj.search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False),('date_start','>=',date_start),('date_stop','<=',date_stop)],order='date_start asc')
    
    def _check_date(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        
        if data['form']['date_from'] > data['form']['date_to']:
            raise osv.except_osv(_('Error !'),('Please select an End Date that is after the Start Date.'))
        sql = """SELECT f.id, f.date_start, f.date_stop
            FROM account_fiscalyear f
            WHERE '%s' = f.id """%(data['form']['fiscalyear'][0])
        cr.execute(sql)
        res = cr.dictfetchall()

        if res:
            if (data['form']['date_to'] > res[0]['date_stop'] or data['form']['date_from'] < res[0]['date_start']):
                raise osv.except_osv(_('UserError'),'The dates need to be between %s and %s' % (res[0]['date_start'], res[0]['date_stop']))
            else:
                return 'report'
        else:
            raise osv.except_osv(_('UserError'),'This fiscal period does not exist.')   
    
    def print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
            
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids[0])
        
        if data['form']['filter'] == 'byperiod':
            del data['form']['date_from']
            del data['form']['date_to']
            data['form']['periods'] = self.period_span(cr, uid, data['form']['periods'], data['form']['fiscalyear'])
        elif data['form']['filter'] == 'bydate':
            self._check_date(cr, uid, data)
            del data['form']['periods']
        elif data['form']['filter'] == 'none':
            del data['form']['date_from']
            del data['form']['date_to']
            del data['form']['periods']
        else:
            self._check_date(cr, uid, data)
            lis2 = str(data['form']['periods']).replace("[","(").replace("]",")")
            sqlmm = """select min(p.date_start) as start, max(p.date_stop) as end 
            from account_period p 
            where p.id in %s"""%lis2
            cr.execute(sqlmm)
            minmax = cr.dictfetchall()
            if minmax:
                if (data['form']['date_to'] < minmax[0]['start']) or (data['form']['date_from'] > minmax[0]['end']):
                    raise osv.except_osv(_('Error !'),_('Empty intersection between the period and date.'))        
               
        return {'type': 'ir.actions.report.xml', 'report_name': 'checks.printed', 'datas': data}
 
check_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: