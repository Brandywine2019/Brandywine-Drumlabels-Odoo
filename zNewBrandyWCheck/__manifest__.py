# coding: utf-8

{
    'name': "Check Customization",
    'author': 'Captivea',
    'website': 'www.captivea.us',
    'version': '12.0.0.0.2',
    'category': 'Sales',
    'summary': """Check Customization""",
    'license': 'AGPL-3',
    'description': """Check Customization""",
    'depends': ['l10n_us_check_printing', 'l10n_ca_check_printing',],
    'data': [
        'report/print_check.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
