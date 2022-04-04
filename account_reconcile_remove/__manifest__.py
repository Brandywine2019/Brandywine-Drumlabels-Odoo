{
    'name': "Account Reconcile Remove",

    'summary': """
        Remove reconcile functionality from Commission report of Account.
        """,

    'description': """
        Remove reconcile functionality from Commission report of Account.
    """,

'author': "",
    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['account_accountant','account_reports'],

    'data': [
            'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
