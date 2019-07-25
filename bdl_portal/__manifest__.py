# -*- coding: utf-8 -*-
{
    'name': ': BDL: Portal Changes',
    'summary': 'Brandywine Drum Labels: Portal Address & Product Access',
    'description': """
task id: 2029052
User acceptance testing :
1:
Grant portal access to a contact. Be prompted to select their access right level [Client User or Client Administrator]
Go to Users in settings and be able to update a contacts access rights.
Log in as a customer who has been granted Client User access rights. They will be able to place an order online, but not be able to create any new shipping or billing addresses beyond what is already assigned to them on the backend.
Log in as a Client Administrator and be able to create new shipping and billing addresses
Both of these contacts can be related to the same company but their access rights are what restrict their capabilities.
2:
Go to website as a non-portal user (or not logged in) and view only published products that are associated with the Public Pricelist
Log-in to the portal as a portal user.
If this portal user has a pricelist associated to their contact card – be able to see all products listed on the respective pricelist
If this portal user has no pricelist associated to their contact card, they will not see any products 
Sales reps on the backend have no restriction to add produts not associated to a specific pricelist / contact
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '0.1',
    'depends': ['sale_management', 'website_sale'],
    'data': [
        'data/data.xml',
        'wizard/portal_wizard_views.xml',
        'views/website_sale_templates.xml',
        'views/sale_order_views.xml',
    ],
}
