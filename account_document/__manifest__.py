{
    "name": "Accounting Documents Management",
    "version": "12.0.1.0.0",
    "author": "Moldeo Interactive,ADHOC SA",
    "license": "AGPL-3",
    "category": "Accounting",
    "depends": [
        "account"
    ],
    "data": [
        'view/account_move_view.xml',
        'view/account_document_type_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
    ],
    'images': [
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
