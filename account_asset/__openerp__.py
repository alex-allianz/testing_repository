# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Allianz Technology (Modified Version of Account_Asset Module (Copyright (C) 2004-2010 Tiny SPRL)).
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
    "name" : "Assets Management",
    "version" : "0",
    "depends" : ["account"],
    "author" : "Allianz Technology",
    "description": """This module manages the assets owned by an entity by keeping track of the depreciation of these assets. It allows the user to create the appropriate depreciation journal entries. 
    DISCLAIMER: This module is a modified version of the module created and certified by OpenERP S.A. (Certificate #: 00146035149029, Copyright (C) 2004-2010 Tiny SPRL)
    
    """,
    "website" : "http://www.allianztechnology.com",
    "category" : "Accounting & Finance",
    "sequence": 32,
    "init_xml" : [ ],
    "demo_xml" : [ ],
    'test': [
        'test/account_asset_demo.yml',
        'test/account_asset.yml',
        'test/account_asset_wizard.yml',
    ],
    "update_xml" : [
        "security/account_asset_security.xml",
        "security/ir.model.access.csv",
        "wizard/account_asset_change_duration_view.xml",
        "wizard/wizard_asset_compute_view.xml",
        "account_asset_view.xml",
        "account_asset_invoice_view.xml",
        "report/account_asset_report_view.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

