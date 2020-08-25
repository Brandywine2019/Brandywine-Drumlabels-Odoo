# -*- coding: utf-8 -*-
{
    'name': "BDL: Website Changes",

    'summary': """
        Brandywine Drum Labels creates custom products for their customers - thus need certain restrictions and features to be available in the portal for it to be functional for them """,

    'description': """
    
Task ID: 2167256 - CIC
        Requirement 1 : 

> Portal User logs in and places an order

> Chooses [any CC] payment acquirer 

> Enters in CC details (or selects token if previous customer)

> Order goes into PENDING - customer receives thank you note

> Log into BACKEND and order is in Quotation - can edit and modify 

> Confirm Sales Order

> Create Invoice 

> Register Payment - Electronic - There is a token available to process against the CC 



Requirement 2:

> Portal User Logs in and places an order

> Payment option page has a 'PO Number' option 

> Clicks on this option - receives a pop up with a text field where user can enter PO Number

> BACKEND - Order is entered as a Quote

>> Order Type = Customer PO

>> Customer Reference has the data brought in from the PO Number payment acquirer 

-- Regular process from here 



>> USER goes to site - is NOT logged into portal -- CANNOT see PO Number Payment Acquirer 


Requirement 4:

>User is at Address Section

>> Only addresses in Billing address are Invoice addresses or parent company address

>>Only addresses in Shipping address are marked as ship to addresses or parent company address

>>>> Client Users (vs Client Admins) can only see their one designated Ship to Address 

>>There is a search bar at the top of Shipping and Billing Addresses

>>>User can enter Name, Street, Street 2, City, Zip and search for an address

>>>>User can select the new Bill or Ship address from this list (boolean field) 

>>Addresses are viewed in list view 
    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'payment'],

    # always loaded
    'data': [
        'data/payment_acquirer_data.xml',
        'views/payment_templates.xml',
        'views/sale_order_views.xml',
        'views/payment_views.xml',
        'views/website_templates.xml',
    ],
    'license': 'OEEL-1',
}
