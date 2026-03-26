{
    'name': 'ADICOPS Restreindre Suppression Paiements',
    'version': '1.0',
    'sequence': 1,
    'category': 'Accounting',
    'summary': 'Restreindre la suppression des paiements à un groupe autorisé',
    'description': "Seuls les utilisateurs du groupe 'Autoriser suppression paiements' peuvent supprimer des paiements.",
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/groups.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
