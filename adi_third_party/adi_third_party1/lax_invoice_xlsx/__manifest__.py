{
    'name': "Invoice Xlsx",
    'summary': """ This module allows to xlsx report of multiple Invoice from the tree/form view.""",
    'author': "Laxicon Solution",
    'website': "www.laxicon.in",
    'sequence': 101,
    'support': 'info@laxicon.in',
    'category': 'Account',
    'version': '15.0.1',
    'license': 'AGPL-3',
    'description': """This module allows to Xlsx Report of Invoice from the tree/form view.
    """,
    'depends': ['account', 'report_xlsx'],
    'data': [
        "report/invoice_xlsx_view.xml",
    ],
    'images':  ["static/description/banner.png"],
    'installable': True,
    'auto_install': False,
    'application': True,
}
