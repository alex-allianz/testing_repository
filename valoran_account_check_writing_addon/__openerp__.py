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
{
    'name': 'Add-on for Check Writing Module',
    'version': '1.2',
    'category': 'Accounting',
    'description': """This extension module improves the functionality of the Check Writing Module (account_check_writing).""",
    'author': 'Allianz Technology',
    'website': 'www.allianztechnology.com',
    'depends': ['account_check_writing', 'purchase'],
    'init_xml': [],
    'update_xml': [
                   'account_check_writing_report.xml',
                   'account_voucher_view.xml',
                   'wizard/check_print_view.xml',
                   'res_currency_view.xml',
                   'account_invoice_view.xml',
                   'account_journal_view.xml',
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
