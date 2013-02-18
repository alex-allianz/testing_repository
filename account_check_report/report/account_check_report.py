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

import time
from report import report_sxw

class check_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(check_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_month': self.get_month,
            'get_fiscalyear_text': self.get_fiscalyear_text,
            'get_periods_and_date_text': self.get_periods_and_date_text
        })
        self.context = context

    def get_month(self, form):
        '''
        Returns day, year and month
        '''
        if form['filter'] in ['bydate', 'all']:
            months=["January","February","March","April","May","June","July","August","September","October","November","December"]
            month = months[time.strptime(form['date_to'],"%Y-%m-%d")[1]-1]
            year = time.strptime(form['date_to'],"%Y-%m-%d")[0]
            day = time.strptime(form['date_to'],"%Y-%m-%d")[2]
            return _('From ')+self.formatLang(form['date_from'], date=True)+ _(' To ')+self.formatLang(form['date_to'], date=True)
        elif form['filter'] in ['byperiod', 'all']:
            aux=[]
            period_obj = self.pool.get('account.period')
                    
            for period in period_obj.browse(self.cr, self.uid, form['periods']):
                aux.append(period.date_from)
                aux.append(period.date_to)
            sorted(aux)
            return _('From ')+self.formatLang(aux[0], date=True)+_(' To ')+self.formatLang(aux[-1], date=True)
    
    def get_fiscalyear_text(self, form):
        """
        Returns the fiscal year text used on the report.
        """
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = None
        
        if form.get('fiscalyear'):
            fiscalyear = fiscalyear_obj.browse(self.cr, self.uid, form['fiscalyear'][0])
            return fiscalyear.name or fiscalyear.code
        
        else:
            fiscalyear = fiscalyear_obj.browse(self.cr, self.uid, fiscalyear_obj.find(self.cr, self.uid))
            return "%s*" % (fiscalyear.name or fiscalyear.code)
        
    def get_periods_and_date_text(self, form):
        """
        Returns the text with the periods/dates used on the report.
        """
        period_obj = self.pool.get('account.period')
        periods_str = None
        fiscalyear_id = form['fiscalyear'] or fiscalyear_obj.find(self.cr, self.uid)
        period_ids = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear_id),('special','=',False)])
        if form['filter'] in ['byperiod', 'all']:
            period_ids = form['periods']
        periods_str = ', '.join([period.name or period.code for period in period_obj.browse(self.cr, self.uid, period_ids)])

        dates_str = None
        if form['filter'] in ['bydate', 'all']:
            dates_str = self.formatLang(form['date_from'], date=True) + ' - ' + self.formatLang(form['date_to'], date=True) + ' '
        return {'periods':periods_str, 'date':dates_str}
    
#    def get_lines(self, form):
#       journal_obj = self.pool.get('account.journal')
#        return journal_obj.browse(self.cr, self.uid, form).journal_id
               

report_sxw.report_sxw('report.checks.printed', 
                      'check.report', 
                      'account_check_report/report/account_check_report.rml',
                       parser=check_report, 
                       header=False)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: