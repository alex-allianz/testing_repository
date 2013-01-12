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
    'version': '1.0',
    'category': 'Accounting',
    'description': """This extension module removes the words "euro" from the amount_to_text field of the Pay Invoice screen and check itself. In addition, it now pulls the content of the "Free Reference" field of the Supplier Invoice. The "Free Reference" Field is the optimal place to record the External Invoice # of the supplier invoices you wish to include in your OpenERP instance.
    """,
    'author': 'Allianz Technology',
    'website': 'www.allianztechnology.com',
    'depends': ['account_check_writing', 'purchase'],
    'init_xml': [],
    'update_xml': [
                   'account_check_writing_report.xml',
                   'account_voucher_view.xml',
                   'res_currency_view.xml',
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
