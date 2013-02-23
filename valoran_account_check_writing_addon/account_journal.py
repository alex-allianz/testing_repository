from osv import osv,fields

class account_journal(osv.osv):
    
    _inherit = 'account.journal'
    
    _columns ={
        'check_sequence_id':fields.many2one('ir.sequence',string='Check Sequence'),
    }
    
account_journal()


class check_log(osv.osv):
    _name = 'check.log'
    _description = 'Check Log'
    '''
        Check Log model
    '''
    _columns = {
        'name':fields.many2one('account.voucher','Reference payment'),
        'status': fields.selection([('active','Active'),
                                    ('voided', 'Voided'),
                                    ('stop_pay', 'Stop Pay Placed'),
                                    ('lost', 'Lost'),
                                    ('unk', 'Unknown'),
                                    ],"Check Status",),
        'check_no':fields.char('Check Number',size=64),
        'cleared': fields.boolean('Cleared', help="Check this if the check is cleared (aka Paid) by the Bank")
        }
    _defaults = {
        'status' :'blank',
    }
check_log()