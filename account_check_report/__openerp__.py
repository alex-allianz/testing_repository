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
{
    "name": 'Check Reporting',
    "version": '1.1',
    'category': 'Reporting',
    'description': """This module generates reports that list the checks written based on date ranges and/or suppliers.""",
    'author': 'Allianz Technology',
    'website': 'www.allianztechnology.com',
    'depends': ['account_check_writing', 'purchase'],
    'init_xml': [],
    'update_xml': [
                   'account_check_report.xml',
                   'wizard/check_report_wizard_view.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: